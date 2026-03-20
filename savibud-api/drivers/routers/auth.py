from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from adapters.ports.user_repository import UserRepository
from drivers.config import settings
from drivers.dependencies import get_repository
from entities.user import Token, TokenData, User
from use_cases.auth import AuthUseCase, RegisterUseCase
from use_cases.exceptions import AlreadyExistingUser

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    # Use the constant as the default fallback
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_refresh_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return TokenData(**payload)
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: UserRepository = Depends(get_repository("user")),
) -> Token:
    try:
        user = AuthUseCase(user_repo)(form_data.username, form_data.password)
        if not user:
            raise Exception("Auth failed")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_payload = {"username": user.username, "user_id": str(user.id)}
    
    return Token(
        access_token=create_access_token(data=token_payload),
        refresh_token=create_refresh_token(data=token_payload),
        token_type="bearer"
    )

@router.post("/token/refresh")
def refresh_access_token(
    refresh_token: str,
    user_repo: UserRepository = Depends(get_repository("user")),
) -> Token:
    token_data = verify_refresh_token(refresh_token)
    
    users = user_repo.read(username=token_data.username)
    if not users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    user = users[0]
    
    token_payload = {"username": user.username, "user_id": str(user.id)}
    
    return Token(
        access_token=create_access_token(data=token_payload),
        refresh_token=create_refresh_token(data=token_payload), # Rotating the refresh token
        token_type="bearer"
    )

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: Request, 
    user_repo: UserRepository = Depends(get_repository("user"))
):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body. Ensure Content-Type is application/json.",
        )

    if not isinstance(body, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Request body must be a JSON object",
        )

    try:
        # Clean up null IDs if present
        if body.get("id") is None:
            body.pop("id", None)
        user_entity = User(**body)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())

    try:
        return RegisterUseCase(user_repo)(user_entity)
    except AlreadyExistingUser as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))