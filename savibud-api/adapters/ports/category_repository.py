from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from adapters.ports.crud import CRUD
from entities.category import Category


class CategoryRepository(CRUD[Category], ABC):
    """Repository to handle categories and budgets"""

    @abstractmethod
    def sum_amount(
        self,
        user_id: UUID,
        period_start: date,
        period_end: date,
        is_fixed: Optional[bool] = None,
        include_incomes: bool = False,
    ) -> Decimal:
        """
        Calculates the total budgeted amount for a user within a specific period.

        Args:
            user_id: The ID of the user.
            period_start: Start date of the budget period.
            period_end: End date of the budget period.
            is_fixed: If True/False, filters by fixed/variable budgets. If None, returns all.
        """

    @abstractmethod
    def sum_amount_spent(
        self,
        user_id: UUID,
        period_start: date,
        period_end: date,
        is_fixed: Optional[bool] = None,
        include_incomes: bool = False,
    ) -> Decimal:
        """
        Calculates the total actual spending recorded against budgets in a period.

        Args:
            user_id: The ID of the user.
            period_start: Start date to check transactions.
            period_end: End date to check transactions.
            is_fixed: Filter spending by fixed or variable budget categories.
        """

    def remaining_bills(
        self, user_id: UUID, period_start: date, period_end: date
    ) -> Decimal:
        """
        Calculates the total amount of fixed budgets (bills) that haven't been spent yet.

        Logic:
        1. Sum all 'fixed' budget amounts for the user.
        2. Sum all transactions that occurred in those 'fixed' categories during this period.
        3. Return (Total Fixed Budgets) - (Absolute value of Actual Spend).
        """
        # 1. Total expected amount for fixed budgets (is_fixed=True)
        total_expected = self.sum_amount(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            is_fixed=True,
        )

        # 2. Total already spent in those fixed categories
        actual_spent = self.sum_amount_spent(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            is_fixed=True,
        )

        # 3. Remaining liability (Expected - Spent)
        remaining = total_expected - actual_spent

        return max(remaining, Decimal(0))

    @abstractmethod
    def get_budget_stats(
        self, 
        user_id: UUID, 
        period_start: date, 
        period_end: date
    ) -> List[Dict[str, Any]]:
        """Returns budget statistics for a user within a specific period."""