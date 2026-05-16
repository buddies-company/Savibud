from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from uuid import UUID

from adapters.ports.crud import CRUD
from entities.saving import SavingsGoal


class SavingsGoalRepository(CRUD[SavingsGoal], ABC):
    """Savings Goal Repository (includes automation functionality)"""

    @abstractmethod
    def sum_target_amount(self, user_id: UUID) -> Decimal:
        """sum of target goals amount"""

    @abstractmethod
    def upsert_account(self, user_id: UUID, account_data: dict):
        """Insert or update a savings account for the user."""

    @abstractmethod
    def get_due_automations(self, user_id: UUID, as_of_date: date) -> list[SavingsGoal]:
        """Retrieve all active automations due on or before the given date."""

    @abstractmethod
    def create_virtual_transaction(
        self, user_id: UUID, goal_id: UUID, amount: Decimal, label: str
    ):
        """Create a virtual transaction for the specified goal."""

    @abstractmethod
    def update_automation_date(self, ugoal_id: UUID, new_date: date):
        """Update the next run date of the specified goal's automation."""

    @abstractmethod
    def get_all_user_ids_with_automations(self) -> list[UUID]:
        """Get a list of all user IDs that have active automations."""
