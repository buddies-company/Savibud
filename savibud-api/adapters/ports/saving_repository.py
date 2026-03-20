from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from adapters.ports.crud import CRUD
from entities.saving import SavingsGoal


class SavingsGoalRepository(CRUD[SavingsGoal], ABC):
    """Savings Goal Repository (includes automation functionality)"""

    @abstractmethod
    def sum_target_amount(self, user_id) -> Decimal:
        """sum of target goals amount"""
        pass

    @abstractmethod
    def upsert_account(self, user_id, account_data):
        """Insert or update a savings account for the user."""
        pass

    @abstractmethod
    def get_due_automations(self, as_of_date: date) -> list[SavingsGoal]:
        """Retrieve all active automations due on or before the given date."""
        pass

    @abstractmethod
    def create_virtual_transaction(self, goal_id, amount, label):
        """Create a virtual transaction for the specified goal."""
        pass

    @abstractmethod
    def update_automation_date(self, goal_id, new_date: date):
        """Update the next run date of the specified goal's automation."""
        pass

