from dataclasses import dataclass

from adapters.ports.user_repository import UserRepository
from drivers.dependencies import pwd_context
from use_cases.exceptions import InvalidPasswordError, UserNotFoundError


@dataclass
class AuthUseCase:
    """Authentication use case"""

    user_repository: UserRepository

    def __call__(self, username: str, password: str) -> None:
        existing_user = self.user_repository.get(username=username)
        if not existing_user:
            raise UserNotFoundError(username)
        if not pwd_context.verify(password, existing_user.hashed_password):
            raise InvalidPasswordError(username)
        return existing_user
