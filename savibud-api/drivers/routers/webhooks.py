# TODO : Implement webhook handling for Powens account synchronization when accessing via internet
import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from adapters.ports.account_repository import AccountRepository
from adapters.ports.transaction_repository import TransactionRepository
from drivers.dependencies import get_repository
from entities.transaction import Transaction

router = APIRouter(prefix="/webhooks")

# Your Secret Key from Powens Console -> Webhooks section
POWENS_WEBHOOK_SECRET = "your_secret_key_here"


def verify_powens_signature(payload: bytes, signature: str):
    """Verify that the webhook actually came from Powens"""
    expected_signature = hmac.new(
        POWENS_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


@router.post("/powens")
async def handle_powens_webhook(
    request: Request,
    bi_signature: str = Header(None),  # Powens sends the signature here
    transaction_repo=Depends(get_repository("transaction")),
    account_repo=Depends(get_repository("account")),
):
    body = await request.body()
    if not verify_powens_signature(body, bi_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("event")  # e.g., "ACCOUNT_SYNCED"

    if event_type == "ACCOUNT_SYNCED":
        account_data = payload.get("data", {})
        powens_account_id = account_data.get("id")

        # Find the account in our DB
        db_accounts = account_repo.read(powens_account_id=powens_account_id)
        if not db_accounts:
            return {"status": "account not found, skipping"}

        db_account = db_accounts[0]

        new_transactions = account_data.get("transactions", [])
        for tx in new_transactions:
            # Idempotency check: don't save duplicates
            if not transaction_repo.read(powens_transaction_id=tx["id"]):
                transaction_repo.create(
                    Transaction(
                        powens_transaction_id=tx["id"],
                        account_id=db_account.id,
                        amount=tx["value"],
                        label=tx["original_wording"],
                        date=tx["date"],
                        raw_data=tx,
                    )
                )

        account_repo.update(db_account.id, balance=account_data.get("balance"))

    return {"status": "success"}
