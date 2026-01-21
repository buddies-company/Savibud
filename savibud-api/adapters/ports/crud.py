from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

# Generic Type for entities
T = TypeVar("T")


class CRUD(Generic[T], ABC):
    """Repository to handle crud"""

    @abstractmethod
    def read(self, **filters) -> List[T]:
        """
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
