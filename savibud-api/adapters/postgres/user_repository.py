from adapters.ports.user_repository import UserRepository as UserRepositoryBase
from adapters.postgres.crud import CRUD
from entities.user import User


class UserRepository(UserRepositoryBase, CRUD):
    """User Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, User)
