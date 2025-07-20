import importlib
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from drivers.config import settings
from entities.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_token_header(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """decode given jwt"""
    try:
        payload: dict = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return TokenData(username=payload.get("sub"))
    except jwt.exceptions.InvalidSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from exc
    except jwt.exceptions.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="token has been expired"
        ) from exc


def get_adapter_repository(name: str, adapter: str = settings.adapter):
    """Retrieve correct adapter class based on name

    name possible values : user
    """
    table_mapping = {"user": {"module": "user_repository", "class": "UserRepository"}}
    try:
        module_name = table_mapping.get(name).get("module")
        class_name = table_mapping.get(name).get("class")
        module = importlib.import_module(f"adapters.{adapter}.{module_name}")
        return getattr(module, class_name)
    except Exception as exc:
        raise NameError(f"Repository for '{name}' not found") from exc
