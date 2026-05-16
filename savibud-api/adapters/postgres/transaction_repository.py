from typing import Optional, List
from datetime import date as date_type, timedelta
from uuid import UUID
from sqlmodel import Session, select, col

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
        offset: int = 0,
    ) -> List[Transaction]:
        statement = select(Transaction).where(Transaction.user_id == user_id)

        if account_id:
            statement = statement.where(Transaction.account_id == account_id)

        if q:
            statement = statement.where(col(Transaction.label).ilike(f"%{q}%"))

        if category_id:
            statement = statement.where(Transaction.category_id == category_id)
        elif savings_goal_id:
            statement = statement.where(Transaction.savings_goal_id == savings_goal_id)
        elif uncategorized_only:
            statement = statement.where(
                Transaction.category_id.is_(None),
                Transaction.savings_goal_id.is_(None),
                ~col(Transaction.is_internal),
            )

        # Date range filtering
        if date_from:
            try:
                statement = statement.where(
                    Transaction.date >= date_type.fromisoformat(date_from)
                )
            except ValueError:
                pass
        if date_to:
            try:
                statement = statement.where(
                    Transaction.date <= date_type.fromisoformat(date_to)
                )
            except ValueError:
                pass

        statement = (
            statement.order_by(col(Transaction.date).desc()).limit(limit).offset(offset)
        )
        return list(self.session.exec(statement).all())

    def get_by_id_and_user(self, tx_id: int, user_id: UUID) -> Optional[Transaction]:
        statement = select(Transaction).where(
            Transaction.id == tx_id, Transaction.user_id == user_id
        )
        return self.session.exec(statement).first()

    def get_unlinked_candidates(
        self, user_id: UUID, days: int = 7
    ) -> List[Transaction]:
        """Fetches transactions that aren't flagged internal within a specific window."""
        cutoff_date = date_type.today() - timedelta(days=days)
        statement = select(Transaction).where(
            Transaction.user_id == user_id,
            ~col(Transaction.is_internal),
            Transaction.internal_link_id.is_(
                None
            ),  # Ensure we don't re-process already linked ones
            Transaction.date >= cutoff_date,
        )
        return list(self.session.exec(statement).all())

    def find_mirror_transaction(
        self, user_id: UUID, source_tx: Transaction, date_window: int = 3
    ) -> Optional[Transaction]:
        """Finds the opposite side of a transfer."""
        start_date = source_tx.date - timedelta(days=date_window)
        end_date = source_tx.date + timedelta(days=date_window)

        statement = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.id != source_tx.id,
            Transaction.account_id
            != source_tx.account_id,  # Cannot be in the same account
            Transaction.amount == -source_tx.amount,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            ~col(Transaction.is_internal),
            Transaction.internal_link_id.is_(None),
        )
        return self.session.exec(statement).first()
