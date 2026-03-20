from datetime import date, datetime, timedelta
from uuid import UUID
from decimal import Decimal

from adapters.ports.account_repository import (
    ManualAccountRepository,
    SnapshotAccountRepository,
)
from entities.account import SnapshotAccount


class GetSnapshotReminder:
    """Use case to check if today is a snapshot day (first Sunday of month)."""

    def is_snapshot_day(self, check_date: date | None = None) -> bool:
        """
        Check if the given date (or today) is the first Sunday of the month.
        Returns True if it is.
        """
        if check_date is None:
            check_date = date.today()
        
        # Find the first day of the month
        first_day = check_date.replace(day=1)
        
        # Find the first Sunday
        days_until_sunday = (6 - first_day.weekday()) % 7
        if days_until_sunday == 0 and first_day.weekday() != 6:
            days_until_sunday = 7
        
        first_sunday = first_day + timedelta(days=days_until_sunday)
        
        return check_date == first_sunday

    def get_user_accounts_for_snapshot(self, user_id: UUID, repo: ManualAccountRepository) -> list:
        """Get all manual accounts that need snapshot updates."""
        return repo.get_user_accounts(user_id)


class RecordAccountSnapshot:
    """Use case to record a snapshot of account balance (for both Powens and manual accounts)."""

    def __init__(
        self,
        account_repo: ManualAccountRepository,
        snapshot_repo: SnapshotAccountRepository,
    ):
        self.account_repo = account_repo
        self.snapshot_repo = snapshot_repo

    def __call__(
        self,
        manual_account_id: UUID | None = None,
        powens_account_id: UUID | None = None,
        user_id: UUID | None = None,
        balance: Decimal | None = None,
        snapshot_date: date | None = None,
    ) -> SnapshotAccount:
        """
        Record a snapshot for an account.
        
        Args:
            manual_account_id: Manual account to snapshot (for manual accounts)
            powens_account_id: Powens account to snapshot (for Powens accounts)
            user_id: User ID (required for recording)
            balance: Current balance to record
            snapshot_date: Date of snapshot (default: today)
        
        Returns:
            Created SnapshotAccount
        """
        if snapshot_date is None:
            snapshot_date = date.today()
        
        if not user_id:
            raise ValueError("user_id is required")
        
        if manual_account_id:
            # Get manual account to verify it exists
            accounts = self.account_repo.read(id=manual_account_id)
            if not accounts:
                raise ValueError(f"Manual account {manual_account_id} not found")
            
            account = accounts[0]
            
            # Update account's current balance
            account.current_balance = balance or account.current_balance
            account.updated_at = datetime.utcnow()
            self.account_repo.update(manual_account_id, current_balance=account.current_balance)
        
        # Create snapshot (supports both account types)
        snapshot = SnapshotAccount(
            account_id=powens_account_id,  # None for manual accounts
            manual_account_id=manual_account_id,  # None for Powens accounts
            user_id=user_id,
            balance=balance or Decimal(0),
            snapshot_date=snapshot_date,
        )
        
        return self.snapshot_repo.create(snapshot)


class GetNetWorthCharts:
    """Use case to get net worth history for charts."""

    def __init__(self, snapshot_repo: SnapshotAccountRepository):
        self.snapshot_repo = snapshot_repo

    def __call__(self, user_id: UUID) -> dict:
        """
        Get net worth history for a user (from all account snapshots - Powens + Manual).
        
        Returns a dict with dates and corresponding total net worth values.
        """
        return self.snapshot_repo.get_user_net_worth_history(user_id)
