from abc import ABC

from adapters.ports.crud import CRUD
from entities.user import User


class UserRepository(CRUD[User], ABC):
    """Repository to handle users"""
