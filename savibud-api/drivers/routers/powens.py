from datetime import datetime
from typing import Annotated
from uuid import UUID

import httpx  # Use httpx for async calls instead of requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from adapters.ports.account_repository import AccountRepository
from adapters.ports.powens_repository import PowensRepository
from adapters.ports.transaction_repository import TransactionRepository
from drivers.config import settings
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.account import Account
from entities.powens import PowensConnection, PowensCred
from entities.transaction import Transaction
from entities.user import User

router = APIRouter(prefix="/powens")


@router.get("/connect")
async def get_powens_connect_url(
    user: User = Depends(connected_user),
    powens_repo: PowensRepository = Depends(get_repository("powens")),
):
    code = ""
    powens_conn = powens_repo.read(user_id=user.id)
    if powens_conn:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{settings.powens_domain}/2.0/auth/token/code",
                headers={
                    "Authorization": f"Bearer {powens_conn[0].powens_access_token}"
                },
            )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Token exchange failed")

        code = response.json().get("code", "")
    params = {
        "client_id": settings.powens_client_id,
        "redirect_uri": settings.powens_redirect_uri,
        "domain": settings.powens_domain,
        "code": code,
        "state": str(user.id),
    }
    base_url = "https://webview.powens.com/connect"
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    print("Generated Powens connect URL:", f"{base_url}?{query_string}")
    return {"url": f"{base_url}?{query_string}"}


@router.post("/exchange_token")
async def exchange_powens_token(
    cred: PowensCred,
    user: User = Depends(connected_user),
    powens_repo: PowensRepository = Depends(get_repository("powens")),
):
    if user.id != UUID(cred.user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")

    powens_conn = powens_repo.read(user_id=user.id)
    if powens_conn:
        return {"status": "connected"}

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
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    data = response.json()

    new_conn = PowensConnection(
        user_id=user.id, powens_access_token=data["access_token"]
    )
    powens_repo.create(new_conn)
    return {"status": "connected"}
