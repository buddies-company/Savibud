from dataclasses import dataclass

from adapters.ports.user_repository import UserRepository
from drivers.dependencies import pwd_context
from entities.user import User
from use_cases.exceptions import (
    AlreadyExistingUser,
    InvalidPasswordError,
    UserNotFoundError,
)


@dataclass
class AuthUseCase:
    """Authentication use case"""

    user_repository: UserRepository

    def __call__(self, username: str, password: str) -> None:
        existing_user = self.user_repository.read(username=username)[0]
        if not existing_user:
            raise UserNotFoundError(username)
        if not pwd_context.verify(password, existing_user.password):
            raise InvalidPasswordError(username)
        return existing_user


@dataclass
class RegisterUseCase:
    """Registration use case"""

    user_repository: UserRepository

    def __call__(self, user: User) -> None:
        existing_user = self.user_repository.read(username=user.username)
        if existing_user:
            raise AlreadyExistingUser(f"User {user.username} already exists")
        user.password = pwd_context.hash(user.password)
        return self.user_repository.create(user)
