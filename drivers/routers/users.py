from typing import Annotated

from fastapi import APIRouter, Depends

from adapters.in_memory.user_repository import InMemoryUserRepository
from drivers.dependencies import get_token_header
from entities.user import User, TokenData

router = APIRouter()


@router.get("/users/me")
def testing_code(token_data: Annotated[TokenData, Depends(get_token_header)]) -> User:
    """Retrieve connected user info"""
    return InMemoryUserRepository().get(username=token_data.username)
