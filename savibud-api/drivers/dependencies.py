import importlib
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from drivers.config import settings
from drivers.database import get_db
from entities.user import TokenData

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
    except jwt.exceptions.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="token has been expired"
        ) from exc


from sqlmodel import Session


def get_adapter_repository(name: str, adapter: str = settings.adapter):
    """Retrieve correct adapter class based on name

    name possible values : user
    """
    table_mapping = {
        "user": {"module": "user_repository", "class": "UserRepository"},
        "saving": {"module": "saving_repository", "class": "SavingsAutomationRepository"},
        "account": {"module": "account_repository", "class": "AccountRepository"},
        "budget": {"module": "budget_repository", "class": "BudgetRepository"},
        "saving_goals":{"module": "saving_repository", "class": "SavingsGoalRepository"},
        "transaction": {
            "module": "transaction_repository",
            "class": "TransactionRepository",
        },
        "category":{"module": "category_repository", "class": "CategoryRepository"},
        "powens": {"module": "powens_repository", "class": "PowensRepository"},
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
