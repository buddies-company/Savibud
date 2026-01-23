from abc import ABC, abstractmethod
from decimal import Decimal

from adapters.ports.crud import CRUD
from entities.saving import SavingsAutomation, SavingsGoal


class SavingsAutomationRepository(CRUD[SavingsAutomation], ABC):
    @abstractmethod
    def upsert_account(self, user_id, account_data):
        """Insert or update a savings account for the user."""
        pass

    @abstractmethod
    def get_due_automations(self, as_of_date) -> list[SavingsAutomation]:
        """Retrieve all active automations due on or before the given date."""
        pass

    @abstractmethod
    def create_virtual_transaction(self, goal_id, amount, label):
        """Create a virtual transaction for the specified goal."""
        pass

    @abstractmethod
    def update_automation_date(self, automation_id, new_date):
        """Update the next run date of the specified automation."""
        pass


class SavingsGoalRepository(CRUD[SavingsGoal], ABC):
    """Saving Goal Repo"""

    @abstractmethod
    def sum_target_amount(self, user_id)->Decimal:
        """sum of target goals amount"""
