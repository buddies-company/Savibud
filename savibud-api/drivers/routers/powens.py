from datetime import datetime
from typing import Annotated
from uuid import UUID

import httpx  # Use httpx for async calls instead of requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from adapters.ports.account_repository import AccountRepository
from adapters.ports.powens_repository import PowensRepository
from adapters.ports.transaction_repository import TransactionRepository
from adapters.powens.client import PowensClient
from drivers.config import settings
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.account import Account
from entities.powens import PowensConnection, PowensCred
from entities.transaction import Transaction
from entities.user import User

router = APIRouter(prefix="/powens")
powens_client = PowensClient(
    client_id=settings.powens_client_id,
    client_secret=settings.powens_client_secret,
    domain=settings.powens_domain,
)


@router.get("/connect")
def get_powens_connect_url(user: User = Depends(connected_user)):
    # Use httpx/urllib to build this safely
    params = {
        "client_id": settings.powens_client_id,
        "redirect_uri": settings.powens_redirect_uri,
        "response_type": "code",
        "state": str(user.id),
        "domain": settings.powens_domain,
    }
    base_url = "https://webview.powens.com/connect"
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    print("Generated Powens connect URL:", f"{base_url}?{query_string}")
    return {"url": f"{base_url}?{query_string}"}


@router.post("/exchange_token")
async def exchange_powens_token(
    cred: PowensCred,
    user: User = Depends(connected_user),
    powens_repo: PowensRepository=Depends(get_repository("powens")),
):
    if user.id != UUID(cred.user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")

    headers = None
    powens_conn = powens_repo.read(user_id=user.id)
    if powens_conn:
        headers={"Authorization": f"Bearer {powens_conn[0].powens_access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://{settings.powens_domain}/2.0/auth/token/access",
            data={
                "grant_type": "authorization_code",
                "code": cred.code,
                "client_id": settings.powens_client_id,
                "client_secret": settings.powens_client_secret,
                "redirect_uri": settings.powens_redirect_uri,
            },
            headers=headers,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    data = response.json()

    if powens_conn:
        # Update existing connection
        powens_repo.update(
            powens_conn[0].id, powens_access_token=data["access_token"]
        )
        return {"status": "updated"}
    else:
        # Save connection
        new_conn = PowensConnection(
            user_id=user.id, powens_access_token=data["access_token"]
        )
        powens_repo.create(new_conn)
        return {"status": "connected"}


async def perform_sync(
    user_id: UUID,
    powens_repo: PowensRepository,
    account_repo: AccountRepository,
    transaction_repo: TransactionRepository,
):
    """The actual heavy lifting logic"""
    conn = powens_repo.read(user_id=user_id)[0]  # Get the token
    if not conn:
        return

    # Fetch accounts
    accounts = await powens_client.get_accounts(conn.powens_access_token)

    for acc in accounts:
        # Upsert Account
        existing = account_repo.read(powens_account_id=acc["id"])
        db_acc_data = {
            "powens_account_id": acc["id"],
            "user_id": user_id,
            "bank_name": acc.get("bank_name", "Unknown"),
            "balance": acc["balance"],
            "raw_data": acc,
        }

        if existing:
            db_account = account_repo.update(existing[0].id, **db_acc_data)
        else:
            db_account = account_repo.create(Account(**db_acc_data))

        if not db_account or not db_account.id:
            continue

        # Fetch Transactions for this account
        txs = await powens_client.get_transactions(conn.powens_access_token, acc["id"])
        for tx in txs:
            # Idempotency check: use powens_transaction_id
            if not transaction_repo.read(powens_transaction_id=tx["id"]):
                transaction_repo.create(
                    Transaction(
                        powens_transaction_id=tx["id"],
                        account_id=db_account.id,
                        amount=tx["value"],  # Powens uses 'value' for amount
                        label=tx["original_wording"],
                        date=tx["date"],
                        raw_data=tx,
                    )
                )


@router.post("/sync")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    user: User = Depends(connected_user),
    powens_repo=Depends(get_repository("powens")),
    account_repo=Depends(get_repository("account")),
    transaction_repo=Depends(get_repository("transaction")),
):
    # Offload the work so the user doesn't wait
    background_tasks.add_task(
        perform_sync, user.id, powens_repo, account_repo, transaction_repo
    )
    return {"message": "Sync started in background"}
