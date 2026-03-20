from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

# Generic Type for entities
T = TypeVar("T")


class CRUD(Generic[T], ABC):
    """Repository to handle crud"""

    @abstractmethod
    def read(self, **filters) -> List[T]:
        r"""
        Fetches records from the database with support for filtering, pagination, and sorting.

        ### Examples:
        ```python
        # Get latest 10 transactions
        repo.read(sort_by="date", order="desc", limit=10)

        # Filter by specific user
        repo.read(user_id="uuid-here", bank_name="Revolut")
        ```

        ### Parameters:
        * **limit** (int, optional): The maximum number of records to return.
        * **offset** (int, optional): The number of records to skip (for pagination).
        * **sort_by** (str, optional): The model attribute name to sort by.
        * **order** (str, optional): The sort direction, either 'asc' (default) or 'desc'.
        * **\*\*filters**: Dynamic keyword arguments matching model attributes for exact filtering.

        ### Returns:
        * `List[T]`: A list of SQLModel instances matching the criteria.
        """

    @abstractmethod
    def create(self, element: T) -> T:
        """Add new element"""

    @abstractmethod
    def update(self, item_id, **modifications) -> T | None:
        """Modify element"""

    @abstractmethod
    def delete(self, item: T) -> bool:
        """Delete element"""

    @abstractmethod
    def upsert(self, element: T, **filters) -> T:
        r"""
        Insert or update a record based on filter criteria (upsert operation).

        If a record matching the filters exists, it will be updated with the values from `element`.
        If no record matches the filters, a new record will be created.

        ### Examples:
        ```python
        # Upsert a transaction by powens_transaction_id and account_id
        transaction = Transaction(
            powens_transaction_id="tx-123",
            account_id="acc-uuid",
            amount=100.00,
            label="Payment"
        )
        repo.upsert(transaction, powens_transaction_id="tx-123", account_id="acc-uuid")

        # Upsert a saving goal by user_id and name
        goal = SavingsGoal(user_id="user-uuid", name="Vacation", target_amount=5000)
        repo.upsert(goal, user_id="user-uuid", name="Vacation")
        ```

        ### Parameters:
        * **element** (T): The entity instance with values to insert or update.
        * **\*\*filters**: Keyword arguments matching model attributes to identify the existing record.
                          If a record with these attribute values exists, it will be updated.
                          Otherwise, a new record will be created with all values from `element`.

        ### Returns:
        * `T`: The created or updated entity instance.
        """
