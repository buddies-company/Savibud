from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import date
from sqlmodel import select, func, or_

from adapters.ports.budget_repository import BudgetRepository as BudgetRepositoryBase
from adapters.postgres.crud import CRUD
from entities.budget import Budget
from entities.category import Category
from entities.transaction import Transaction
from entities.account import Account

class BudgetRepository(BudgetRepositoryBase, CRUD):
    """Budget Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, Budget)

    def sum_amount(
        self, 
        user_id: UUID, 
        period_start: date, 
        period_end: date, 
        is_fixed: Optional[bool] = None,
        include_incomes: bool=False
    ) -> Decimal:
        """
        Calculates the total budgeted amount for a user within a specific period.
        
        Args:
            user_id: The ID of the user.
            period_start: Start date of the budget period.
            period_end: End date of the budget period.
            is_fixed: If True/False, filters by fixed/variable budgets. If None, returns all.
        """
        statement = select(func.sum(Budget.amount))

        if not include_incomes:
            statement = statement.join(Category).where(Category.is_income == False)

        statement = statement.where(
            Budget.user_id == user_id,
            or_(Budget.start_date == None, Budget.start_date >= period_start),
            or_(Budget.end_date == None, Budget.end_date <= period_end)
        )

        if is_fixed is not None:
            statement = statement.where(Budget.is_fixed == is_fixed)

        result = self.session.exec(statement).one()
        return Decimal(result) if result else Decimal(0)

    def sum_amount_spent(
        self, 
        user_id: UUID, 
        period_start: date, 
        period_end: date, 
        is_fixed: Optional[bool] = None,
        include_incomes: bool=False
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
            .join(Budget, Transaction.category_id == Budget.category_id)
        )

        if not include_incomes:
            statement = statement.join(Category).where(Category.is_income == False)
            
        statement = statement.where(
                Budget.user_id == user_id,
                Account.user_id == user_id,
                Transaction.amount <= 0,
                Transaction.date >= period_start,
                Transaction.date <= period_end,
                or_(Budget.start_date == None, Budget.start_date >= period_start),
                or_(Budget.end_date == None, Budget.end_date <= period_end)
            )

        if is_fixed is not None:
            statement = statement.where(Budget.is_fixed == is_fixed)

        result = self.session.exec(statement).one()
        return abs(Decimal(result)) if result else Decimal(0)

        """
        Calculates the total amount of fixed budgets (bills) that haven't been spent yet.
        
        Uses sum_amount and sum_amount_spent specifically for 'fixed' items to determine
        outstanding liabilities for the current period.
        """
        # 1. Total expected amount for fixed budgets (is_fixed=True)
        total_expected = self.sum_amount(
            user_id=user_id, 
            period_start=period_start, 
            period_end=period_end, 
            is_fixed=True
        )

        # 2. Total already spent in those fixed categories
        actual_spent = self.sum_amount_spent(
            user_id=user_id, 
            period_start=period_start, 
            period_end=period_end, 
            is_fixed=True
        )

        # 3. Remaining liability (Expected - Spent)
        remaining = total_expected - actual_spent
        
        return max(remaining, Decimal(0))