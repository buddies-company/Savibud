from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session, select, func, or_
from dateutil.relativedelta import relativedelta

from adapters.ports.account_repository import (
    ManualAccountRepository as ManualAccountRepositoryInterface,
    SnapshotAccountRepository as SnapshotAccountRepositoryInterface,
)
from adapters.postgres.crud import CRUD
from entities.account import ManualAccount, SnapshotAccount


class ManualAccountRepository(ManualAccountRepositoryInterface, CRUD[ManualAccount]):
    """PostgreSQL implementation for manual accounts."""

    def __init__(self, session: Session):
        super().__init__(session, ManualAccount)

    def get_user_accounts(self, user_id: UUID) -> list[ManualAccount]:
        """Get all manual accounts for a user."""
        statement = select(ManualAccount).where(ManualAccount.user_id == user_id)
        return list(self.session.exec(statement).all())

    def calculate_loan_balance(self, account: ManualAccount) -> float:
        """
        Calculate remaining balance for a loan using amortization formula.
        
        Formula: Remaining Balance = P * [(1 + r)^n - (1 + r)^p] / [(1 + r)^n - 1]
        where:
        - P = Initial loan amount
        - r = Monthly interest rate (annual / 12)
        - n = Total number of payments (duration in months)
        - p = Number of payments made
        """
        if account.account_type != "loan" or not account.loan_start_date:
            return float(account.current_balance)

        P = float(account.loan_initial_amount or 0)
        annual_rate = float(account.loan_interest_rate or 0) / 100
        monthly_rate = annual_rate / 12
        n = account.loan_duration_months or 1
        
        # Calculate months elapsed since loan start
        months_elapsed = (datetime.now().date() - account.loan_start_date).days // 30
        p = min(months_elapsed, n)  # Can't exceed total duration
        
        if monthly_rate == 0:
            # Simple case: no interest
            return max(P - (P / n) * p, 0)
        
        # Amortization formula
        numerator = (1 + monthly_rate) ** n - (1 + monthly_rate) ** p
        denominator = (1 + monthly_rate) ** n - 1
        
        if denominator == 0:
            return P
        
        remaining = P * (numerator / denominator)
        return max(float(remaining), 0)


class SnapshotAccountRepository(SnapshotAccountRepositoryInterface, CRUD[SnapshotAccount]):
    """PostgreSQL implementation for account snapshots (supports both Powens and manual accounts)."""

    def __init__(self, session: Session):
        super().__init__(session, SnapshotAccount)

    def get_latest_snapshot(
        self, 
        account_id: UUID | None = None, 
        manual_account_id: UUID | None = None
    ) -> SnapshotAccount | None:
        """Get the most recent snapshot for an account (either Powens or manual)."""
        query = select(SnapshotAccount)
        
        if account_id and manual_account_id:
            query = query.where(
                or_(
                    SnapshotAccount.account_id == account_id,
                    SnapshotAccount.manual_account_id == manual_account_id,
                )
            )
        elif account_id:
            query = query.where(SnapshotAccount.account_id == account_id)
        elif manual_account_id:
            query = query.where(SnapshotAccount.manual_account_id == manual_account_id)
        
        statement = query.order_by(SnapshotAccount.snapshot_date.desc()).limit(1)
        return self.session.exec(statement).first()

    def get_snapshots_for_period(
        self, 
        start_date: date, 
        end_date: date,
        account_id: UUID | None = None, 
        manual_account_id: UUID | None = None
    ) -> list[SnapshotAccount]:
        """Get snapshots for an account within a date range."""
        query = select(SnapshotAccount).where(
            SnapshotAccount.snapshot_date >= start_date,
            SnapshotAccount.snapshot_date <= end_date,
        )
        
        if account_id and manual_account_id:
            query = query.where(
                or_(
                    SnapshotAccount.account_id == account_id,
                    SnapshotAccount.manual_account_id == manual_account_id,
                )
            )
        elif account_id:
            query = query.where(SnapshotAccount.account_id == account_id)
        elif manual_account_id:
            query = query.where(SnapshotAccount.manual_account_id == manual_account_id)
        
        statement = query.order_by(SnapshotAccount.snapshot_date.asc())
        return list(self.session.exec(statement).all())

    def get_user_net_worth_history(self, user_id: UUID) -> dict:
        """
        Calculate net worth over time from all account snapshots (Powens + Manual).
        Groups by snapshot_date and sums all account balances.
        """
        statement = (
            select(
                SnapshotAccount.snapshot_date,
                func.sum(SnapshotAccount.balance).label("total_balance")
            )
            .where(SnapshotAccount.user_id == user_id)
            .group_by(SnapshotAccount.snapshot_date)
            .order_by(SnapshotAccount.snapshot_date.asc())
        )
        
        results = self.session.exec(statement).all()
        return {
            "dates": [str(row[0]) for row in results],
            "net_worths": [float(row[1]) for row in results],
        }
