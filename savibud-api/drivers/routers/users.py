from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from adapters.ports.user_repository import UserRepository
from drivers.dependencies import get_repository, get_token_header
from entities.user import TokenData, User
from use_cases.auth import RevokeUseCase
from use_cases.exceptions import UserNotFoundError

router = APIRouter()


@router.get("/users/me")
def connected_user(
    token_data: Annotated[TokenData, Depends(get_token_header)],
    user_repo: UserRepository = Depends(get_repository("user")),
) -> User:
    """Retrieve connected user info"""
    users = user_repo.read(username=token_data.username)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]


@router.delete("/users/me")
def revoke_user(
    user: User = Depends(connected_user),
    user_repo: UserRepository = Depends(get_repository("user")),
):
    """Revoke a user"""
    try:
        return RevokeUseCase(user_repo)(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
