from unittest.mock import PropertyMock, patch

import pytest

from adapters.in_memory.user_repository import UserRepository
from adapters.ports.user_repository import UserRepository as UserRepositoryBase
from entities.user import User
from use_cases.auth import AuthUseCase, RegisterUseCase
from use_cases.exceptions import (
    AlreadyExistingUser,
    InvalidPasswordError,
    UserNotFoundError,
)


@pytest.fixture
def users_repository() -> UserRepositoryBase:
    """Retrieve in memory user repository class"""
    return UserRepository()


@pytest.fixture
def auth_use_case(users_repository: UserRepositoryBase) -> AuthUseCase:
    """Initialisation of AuthUseCase class"""
    return AuthUseCase(users_repository)


@pytest.fixture
def register_use_case(users_repository: UserRepositoryBase) -> RegisterUseCase:
    """Initialisation of RegisterUseCase class"""
    return RegisterUseCase(users_repository)


def test_user_not_found(auth_use_case: AuthUseCase):
    """try to connect to non existing user"""
    with pytest.raises(UserNotFoundError):
        auth_use_case("not found", "password")


def test_wrong_password(auth_use_case: AuthUseCase):
    """try to connect with wrong password"""
    with patch(
        "adapters.in_memory.user_repository.UserRepository.data",
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
        "adapters.in_memory.user_repository.UserRepository.data",
        new_callable=PropertyMock,
        return_value=[user],
    ):
        connected = auth_use_case("johndoe", "secret")
    assert connected == user


def test_register_existing_user(register_use_case: RegisterUseCase):
    existing_user = User(
        "johndoe", "test_password_hash"  # This should be a hashed password
    )
    with patch(
        "adapters.in_memory.user_repository.UserRepository.data",
        new_callable=PropertyMock,
        return_value=[existing_user],
    ):
        with pytest.raises(AlreadyExistingUser):
            register_use_case(existing_user)


def test_register_new_user(
    auth_use_case: AuthUseCase, register_use_case: RegisterUseCase
):
    """try to register a new user"""
    new_user = User("janedoe", "secret")
    new_user = register_use_case(new_user)
    connected = auth_use_case("janedoe", "secret")
    assert connected == new_user


def test_password_is_hashed_on_register(register_use_case: RegisterUseCase):
    """Ensure that the password is hashed when registering a new user"""
    plain_password = "mysecret"
    new_user = User("alice", plain_password)
    registered_user:User = register_use_case(new_user)
    # The stored password should not be the same as the plain password
    assert registered_user.password != plain_password
    # The stored password should look like a bcrypt hash
    assert registered_user.password.startswith("$2b$")
