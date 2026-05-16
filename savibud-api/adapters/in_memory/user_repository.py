from adapters.in_memory.crud import CRUD
from adapters.ports.user_repository import UserRepository as UserRepositoryBase
from entities.user import User


class UserRepository(UserRepositoryBase, CRUD):
    """User Repository using in memory data"""

    data: list[User] = [
        User(username="johndoe", password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
    ]

    def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        return next((user for user in self.data if user.username == username), None)
    
    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID"""
        return next((user for user in self.data if str(user.id) == user_id), None)
    
    def list(self) -> list[User]:
        """List all users"""
        return self.data