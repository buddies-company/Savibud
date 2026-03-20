from typing import Optional
from datetime import date as date_type
from uuid import UUID
from sqlmodel import Session, select

from adapters.ports.transaction_repository import (
    TransactionRepository as TransactionRepositoryBase,
)
from adapters.postgres.crud import CRUD
from entities.transaction import Transaction


class TransactionRepository(TransactionRepositoryBase, CRUD):
    """Transaction Repository using Postgres (SQLModel) data"""

    def __init__(self, session: Session):
        super().__init__(session, Transaction)

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
    ):
        # Build base query with ownership check
        statement = select(Transaction).where(Transaction.user_id == user_id)

        if account_id:
            statement = statement.where(Transaction.account_id == account_id)

        # Apply SQL-level LIKE filtering
        if q:
            statement = statement.where(Transaction.label.ilike(f"%{q}%"))
        
        if category_id:
            statement = statement.where(Transaction.category_id == category_id)
        elif savings_goal_id:
            statement = statement.where(Transaction.savings_goal_id == savings_goal_id)
        elif uncategorized_only:
            statement = statement.where(Transaction.category_id.is_(None) & Transaction.savings_goal_id.is_(None) & Transaction.is_internal.is_(False))
        
        # Apply date range filtering
        if date_from:
            try:
                from_date = date_type.fromisoformat(date_from)
                statement = statement.where(Transaction.date >= from_date)
            except ValueError:
                pass  # Invalid date format, skip this filter
        
        if date_to:
            try:
                to_date = date_type.fromisoformat(date_to)
                statement = statement.where(Transaction.date <= to_date)
            except ValueError:
                pass  # Invalid date format, skip this filter

        # Apply pagination and ordering
        statement = statement.order_by(Transaction.date.desc()).limit(limit).offset(offset)
        
        return list(self.session.exec(statement).all())

    def get_by_id_and_user(self, tx_id: int, user_id: UUID) -> Optional[Transaction]:
        # Securely fetch a transaction belonging to a specific user
        statement = select(Transaction).where(Transaction.id == tx_id, Transaction.user_id == user_id)
        return self.session.exec(statement).first()