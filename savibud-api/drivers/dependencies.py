import importlib
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session

from adapters.ports.account_repository import (
    AccountRepository,
    SnapshotAccountRepository,
)
from adapters.ports.powens_repository import PowensRepository
from adapters.ports.saving_repository import SavingsGoalRepository
from adapters.ports.transaction_repository import TransactionRepository
from adapters.powens.client import PowensClient
from drivers.config import settings
from drivers.database import get_db
from entities.user import TokenData, User
from use_cases.sync_powens_user import SyncUserData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_token_header(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """decode given jwt"""
    try:
        payload: dict = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenData(**payload)
    except jwt.exceptions.InvalidSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from exc
    except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="token has been expired"
        ) from exc


def get_adapter_repository(name: str, adapter: str = settings.adapter):
    """Retrieve correct adapter class based on name

    name possible values : user
    """
    table_mapping = {
        "user": {"module": "user_repository", "class": "UserRepository"},
        "saving": {
            "module": "saving_repository",
            "class": "SavingsGoalRepository",
        },
        "account": {"module": "account_repository", "class": "AccountRepository"},
        "saving_goals": {
            "module": "saving_repository",
            "class": "SavingsGoalRepository",
        },
        "transaction": {
            "module": "transaction_repository",
            "class": "TransactionRepository",
        },
        "category": {"module": "category_repository", "class": "CategoryRepository"},
        "powens": {"module": "powens_repository", "class": "PowensRepository"},
        "snapshot_account": {
            "module": "manual_account_repository",
            "class": "SnapshotAccountRepository",
        },
        "rule": {"module": "rule_repository", "class": "RuleRepository"},
        "manual_accounts": {
            "module": "manual_account_repository",
            "class": "ManualAccountRepository",
        },
    }
    try:
        module_name = table_mapping.get(name, {}).get("module")
        class_name = table_mapping.get(name, {}).get("class", "")
        module = importlib.import_module(f"adapters.{adapter}.{module_name}")
        return getattr(module, class_name)
    except Exception as exc:
        raise NameError(f"Repository for '{name}' not found") from exc


def get_repository(name: str):
    """Return a dependency factory that provides a repository instance tied to a DB session."""

    def _get_repo(db: Annotated[Session, Depends(get_db)]):
        RepoClass = get_adapter_repository(name)
        return RepoClass(db)

    return _get_repo

def get_connected_user_local():
    from drivers.routers.users import connected_user
    return connected_user

def get_powens_client(
    user: User = Depends(get_connected_user_local()),
    powens_repo: PowensRepository = Depends(get_repository("powens")),
):
    """Create and return a PowensClient instance with the current user's access token."""
    connection = powens_repo.read(user_id=user.id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No Powens connection found for user",
        )
    return PowensClient(
        access_token=connection[0].powens_access_token,
        domain=settings.powens_domain,
    )


def get_sync_user(
    powens_client: PowensClient = Depends(get_powens_client),
    repo: SavingsGoalRepository = Depends(get_repository("saving")),
    powens_repo: PowensRepository = Depends(get_repository("powens")),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
    account_repo: AccountRepository = Depends(get_repository("account")),
    snapshot_account_repo: SnapshotAccountRepository = Depends(
        get_repository("snapshot_account")
    ),
    rule_repo = Depends(get_repository("rule")),
    savings_goal_repo = Depends(get_repository("saving_goals")),
):
    return SyncUserData(
        powens_client=powens_client,
        repo=repo,
        powens_repo=powens_repo,
        transaction_repo=transaction_repo,
        account_repo=account_repo,
        snapshot_account_repo=snapshot_account_repo,
        rule_repo=rule_repo,
        savings_goal_repo=savings_goal_repo,
    )
