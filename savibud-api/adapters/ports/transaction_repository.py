from abc import ABC, abstractmethod

from adapters.ports.crud import CRUD
from entities.transaction import Transaction


class TransactionRepository(CRUD[Transaction], ABC):
    """Repository to handle transactions"""

    @abstractmethod
    def upsert_transaction(self, account_id, transaction_data):
        """Insert or update a transaction for the given account."""
        pass