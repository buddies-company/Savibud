from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from adapters.ports.user_repository import UserRepository
from entities.user import TokenData, User
from use_cases.auth import RevokeUseCase
from use_cases.exceptions import UserNotFoundError

router = APIRouter()


def get_token_header_local():
    """Lazy import to avoid circular dependency."""
    from drivers.dependencies import get_token_header
    return get_token_header


def get_repository_local(repo_name: str):
    """Lazy import to avoid circular dependency."""
    from drivers.dependencies import get_repository
    return get_repository(repo_name)


def connected_user(
    token_data: Annotated[TokenData, Depends(get_token_header_local())],
    user_repo: UserRepository = Depends(get_repository_local("user")),
) -> User:
    """Retrieve connected user info"""
    users = user_repo.read(username=token_data.username)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]


@router.get("/users/me")
def get_connected_user(
    user: User = Depends(connected_user),
) -> User:
    """Retrieve connected user info"""
    return user


@router.delete("/users/me")
def revoke_user(
    user: User = Depends(connected_user),
    user_repo: UserRepository = Depends(get_repository_local("user")),
):
    """Revoke a user"""
    try:
        return RevokeUseCase(user_repo)(user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
