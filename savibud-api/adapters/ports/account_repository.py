"""Defines repository interfaces for account-related data operations, including:
- AccountRepository: CRUD operations for accounts.
- SnapshotAccountRepository: CRUD operations for account snapshots, plus methods to retrieve latest snapshots and net worth history.
- ManualAccountRepository: CRUD operations for manual accounts, plus methods to calculate loan balances.
These repositories abstract away the underlying data storage and provide a consistent interface
for the application to interact with account data."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from adapters.ports.crud import CRUD
from entities.account import Account, SnapshotAccount, ManualAccount


class AccountRepository(CRUD[Account], ABC):
    """Repository to handle accounts"""


class SnapshotAccountRepository(CRUD[SnapshotAccount], ABC):
    """
    Repository to handle account snapshots.
    Supports snapshots for both Powens accounts and manual accounts.
    """

    @abstractmethod
    def get_latest_snapshot(
        self, account_id: UUID | None = None, manual_account_id: UUID | None = None
    ) -> SnapshotAccount | None:
        """Get the most recent snapshot for an account (either Powens or manual)."""

    @abstractmethod
    def get_snapshots_for_period(
        self,
        start_date: date,
        end_date: date,
        account_id: UUID | None = None,
        manual_account_id: UUID | None = None,
    ) -> list[SnapshotAccount]:
        """Get snapshots for an account within a date range."""

    @abstractmethod
    def get_user_net_worth_history(self, user_id: UUID) -> dict:
        """Calculate net worth over time from all account snapshots (Powens + Manual)."""


class ManualAccountRepository(CRUD[ManualAccount], ABC):
    """Repository for manual accounts (loans and savings)."""

    @abstractmethod
    def get_user_accounts(self, user_id: UUID) -> list[ManualAccount]:
        """Get all manual accounts for a user."""

    @abstractmethod
    def calculate_loan_balance(self, account: ManualAccount) -> float:
        """Calculate remaining balance for a loan account."""
