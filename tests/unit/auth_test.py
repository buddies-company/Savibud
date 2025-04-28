from unittest.mock import PropertyMock, patch

import pytest

from adapters.in_memory.user_repository import InMemoryUserRepository
from adapters.ports.user_repository import UserRepository
from entities.user import User
from use_cases.auth import AuthUseCase
from use_cases.exceptions import InvalidPasswordError, UserNotFoundError


@pytest.fixture
def users_repository() -> UserRepository:
    """Retrieve in memory user repository class"""
    return InMemoryUserRepository()


@pytest.fixture
def auth_use_case(users_repository: UserRepository) -> AuthUseCase:
    """Initialisation of AuthUseCase class"""
    return AuthUseCase(users_repository)


def test_user_not_found(auth_use_case: AuthUseCase):
    """try to connect to non existing user"""
    with pytest.raises(UserNotFoundError):
        auth_use_case("not found", "password")


def test_wrong_password(auth_use_case: AuthUseCase):
    """try to connect with wrong password"""
    with patch(
        "adapters.in_memory.user_repository.InMemoryUserRepository.users",
        new_callable=PropertyMock,
        return_value=[
            User(
                "johndoe",
                "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            )
        ],
    ):
        with pytest.raises(InvalidPasswordError):
            auth_use_case("johndoe", "wrong password")


def test_connection_success(auth_use_case: AuthUseCase):
    """try to connect to existing user"""
    user = User(
        "johndoe", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    with patch(
        "adapters.in_memory.user_repository.InMemoryUserRepository.users",
        new_callable=PropertyMock,
        return_value=[user],
    ):
        connected = auth_use_case("johndoe", "secret")
    assert connected == user
