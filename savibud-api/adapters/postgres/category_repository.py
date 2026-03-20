from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import func, or_, select

from adapters.ports.category_repository import (
    CategoryRepository as CategoryRepositoryBase,
)
from adapters.postgres.crud import CRUD
from entities.account import Account
from entities.category import Category
from entities.transaction import Transaction


class CategoryRepository(CategoryRepositoryBase, CRUD):
    """Category Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, Category)

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
        statement = select(func.sum(Category.budget_amount))

        if not include_incomes:
            statement = statement.where(Category.is_income == False)

        statement = statement.where(
            Category.user_id == user_id,
            Category.budget_amount != None,
            or_(Category.budget_start_date == None, Category.budget_start_date >= period_start),
            or_(Category.budget_end_date == None, Category.budget_end_date <= period_end),
        )

        if is_fixed is not None:
            statement = statement.where(Category.is_fixed == is_fixed)

        result = self.session.exec(statement).one()
        return Decimal(result) if result else Decimal(0)

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
        statement = (
            select(func.sum(Transaction.amount))
            .join(Account)
            .join(Category, Transaction.category_id == Category.id)
        )

        if not include_incomes:
            statement = statement.where(Category.is_income == False)

        statement = statement.where(
            Category.user_id == user_id,
            Account.user_id == user_id,
            Transaction.amount <= 0,
            Transaction.date >= period_start,
            Transaction.date <= period_end,
            Category.budget_amount != None,
            or_(Category.budget_start_date == None, Category.budget_start_date >= period_start),
            or_(Category.budget_end_date == None, Category.budget_end_date <= period_end),
        )

        if is_fixed is not None:
            statement = statement.where(Category.is_fixed == is_fixed)

        result = self.session.exec(statement).one()
        return abs(Decimal(result)) if result else Decimal(0)

    def get_budget_stats(
        self, 
        user_id: UUID, 
        period_start: date, 
        period_end: date
    ) -> List[Dict[str, Any]]:
        """
        Returns spent and remaining amounts per category for a specific window.
        """
        # Sum transactions grouped by category
        statement = (
            select(
                Category.id,
                func.sum(Transaction.amount).label("spent")
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .where(
                Category.user_id == user_id,
                Transaction.date >= period_start,
                Transaction.date <= period_end
            )
            .group_by(Category.id)
        )
        
        results = self.session.exec(statement).all()
        # Map results to a dictionary for easy frontend consumption
        return [{"category_id": str(r.id), "spent": abs(float(r.spent))} for r in results]