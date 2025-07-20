from adapters.in_memory.crud import CRUD
from adapters.ports.user_repository import UserRepository as UserRepositoryBase
from entities.user import User


class UserRepository(UserRepositoryBase, CRUD):
    """User Repository using in memory data"""

    data: list[User] = [
        User("johndoe", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
    ]
