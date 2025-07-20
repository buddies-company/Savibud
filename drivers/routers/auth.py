from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from adapters.ports.user_repository import UserRepository
from drivers.config import settings
from drivers.dependencies import get_adapter_repository
from entities.user import Token, User
from use_cases.auth import AuthUseCase, RegisterUseCase
from use_cases.exceptions import AlreadyExistingUser

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Encode data into JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Connect user via form data and retrieve JWT"""
    user_repo: UserRepository = get_adapter_repository("user")
    user: User = AuthUseCase(user_repo())(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/auth/register", status_code=201)
def register(item: User):
    """Register a new user"""
    user_repo: UserRepository = get_adapter_repository("user")
    try:
        return RegisterUseCase(user_repo())(item)
    except AlreadyExistingUser as e:
        raise HTTPException(status_code=409, detail=str(e))
