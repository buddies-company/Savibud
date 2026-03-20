from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from adapters.ports.crud import CRUD
from entities.transaction import Transaction


class TransactionRepository(CRUD[Transaction], ABC):
    """Repository to handle transactions"""

    @abstractmethod
    def get_user_transactions(
        self, 
        user_id: UUID, 
        q: Optional[str] = None,
        account_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        savings_goal_id: Optional[UUID] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        uncategorized_only: bool = False,
        limit: int = 20,
        offset: int = 0
    )-> list[Transaction]:
        """Fetch transactions for a user with optional filters and pagination"""

    @abstractmethod
    def get_by_id_and_user(self, tx_id: int, user_id: UUID) -> Optional[Transaction]:
        """Fetch a transaction by ID ensuring it belongs to the specified user"""