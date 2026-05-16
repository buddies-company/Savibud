from adapters.ports.account_repository import AccountRepository as AccountRepositoryBase
from adapters.postgres.crud import CRUD
from entities.account import Account


class AccountRepository(AccountRepositoryBase, CRUD[Account]):
    """Account Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, Account)
