from adapters.ports.user_repository import UserRepository
from entities.user import User


class InMemoryUserRepository(UserRepository):
    """User Repository using in memory data"""

    users: list[User] = [
        User("johndoe", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
    ]

    def get(self, username) -> User | None:
        for user in self.users:
            if username == user.username:
                return user
        return None
