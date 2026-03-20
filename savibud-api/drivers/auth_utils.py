"""Authentication utilities and dependency functions."""
from typing import Annotated

from fastapi import Depends, HTTPException

from adapters.ports.user_repository import UserRepository
from entities.user import TokenData, User


def get_connected_user(
    token_data: Annotated[TokenData, Depends(None)],
    user_repo: UserRepository = Depends(None),
) -> User:
    """Retrieve connected user info from token and repository."""
    users = user_repo.read(username=token_data.username)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]
