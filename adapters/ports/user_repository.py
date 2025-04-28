from abc import ABC, abstractmethod

from entities.user import User


class UserRepository(ABC):
    """Repository to handle users"""

    @abstractmethod
    def get(self, username: str) -> User | None:
        """Rtrieve a user based on username"""
