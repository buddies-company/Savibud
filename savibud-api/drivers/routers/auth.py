from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from adapters.ports.user_repository import UserRepository
from drivers.config import settings
from drivers.dependencies import get_repository
from entities.user import Token, User
from use_cases.auth import AuthUseCase, RegisterUseCase
from use_cases.exceptions import AlreadyExistingUser

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 3600


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
    user_repo: UserRepository = Depends(get_repository("user")),
) -> Token:
    """Connect user via form data and retrieve JWT"""
    try:
        user: User | None = AuthUseCase(user_repo)(
            form_data.username, form_data.password
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    access_token = create_access_token(
        data={"username": user.username, "user_id": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


from fastapi import Request
from pydantic import ValidationError


@router.post("/auth/register", status_code=201)
async def register(
    request: Request, user_repo: UserRepository = Depends(get_repository("user"))
):
    """Register a new user.

    This endpoint reads the JSON body explicitly so we can return a clearer error
    when clients send an invalid payload (for example when the client sends the
    string "[object Object]" instead of valid JSON).
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body. Make sure the request Content-Type is application/json and the body is valid JSON.",
        )

    # Ensure body is a mapping/dict so SQLModel/Pydantic can parse fields
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request body must be a JSON object/dictionary with user fields",
        )

    try:
        if "id" in body and body["id"] is None:
            del body["id"]
        user = User(**body)
    except ValidationError as e:
        # Return helpful validation errors from Pydantic
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
        )

    try:
        return RegisterUseCase(user_repo)(user)
    except AlreadyExistingUser as e:
        raise HTTPException(status_code=409, detail=str(e))
