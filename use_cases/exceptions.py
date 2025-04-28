# pylint: disable=missing-class-docstring
from dataclasses import dataclass


@dataclass
class UserNotFoundError(Exception):
    username: str

    def __str__(self) -> str:
        return f"User not found: {self.username}"


@dataclass
class InvalidPasswordError(Exception):
    username: str

    def __str__(self) -> str:
        return f"Invalid password for user: {self.username}"
