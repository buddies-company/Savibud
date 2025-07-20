from typing import Annotated

from fastapi import APIRouter, Depends

from adapters.ports.user_repository import UserRepository
from drivers.dependencies import get_adapter_repository, get_token_header
from entities.user import TokenData, User

router = APIRouter()


@router.get("/users/me")
def connected_user(token_data: Annotated[TokenData, Depends(get_token_header)]) -> User:
    """Retrieve connected user info"""
    user_repo: UserRepository = get_adapter_repository("user")()
    return user_repo.read(username=token_data.username)[0]
