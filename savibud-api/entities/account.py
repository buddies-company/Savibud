from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    """Account entity representing a user's bank account synced via Powens."""

    __tablename__ = "accounts"
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    powens_account_id: str = Field(index=True, nullable=False, unique=True)
    name: str = Field(max_length=255)
    bank_name: str
    account_type: str  # e.g., "checking", "savings"
    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="EUR")
    last_sync: Optional[datetime] = None
    is_active: bool = Field(default=True)
    raw_data: Optional[dict] = Field(default={}, sa_type=JSONB)


class SnapshotAccount(SQLModel, table=True):
    """
    Snapshot of account balance for tracking history.
    Can store snapshots for both Powens accounts and manual accounts.
    """
    __tablename__ = "snapshot_accounts"
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    
    # Source account (one must be set)
    account_id: Optional[UUID] = Field(default=None, foreign_key="accounts.id", ondelete="CASCADE")
    manual_account_id: Optional[UUID] = Field(default=None, foreign_key="manual_accounts.id", ondelete="CASCADE")
    
    # Common fields
    user_id: UUID = Field(foreign_key="users.id")
    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    snapshot_date: date  # The date of the snapshot
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class ManualAccount(SQLModel, table=True):
    """Manual account for loans and savings (not synced from banks)."""
    __tablename__ = "manual_accounts"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    name: str  # e.g., "Home Loan", "Savings Account"
    account_type: str  # 'loan' or 'savings'
    current_balance: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(default="EUR", max_length=3)
    
    # Loan-specific fields
    loan_initial_amount: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    loan_interest_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=3)  # Annual percentage
    loan_duration_months: Optional[int] = Field(default=None)  # Total loan duration
    loan_start_date: Optional[date] = Field(default=None)
    loan_monthly_payment: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)  # Calculated
    
    # Metadata
    icon: Optional[str] = Field(default="BanknotesIcon", max_length=100)
    color: str = Field(default="#3b82f6", max_length=7)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ManualAccountRead(SQLModel):
    """Schema for reading manual accounts."""
    id: UUID
    user_id: UUID
    name: str
    account_type: str
    current_balance: Decimal
    currency: str
    loan_initial_amount: Optional[Decimal]
    loan_interest_rate: Optional[Decimal]
    loan_duration_months: Optional[int]
    loan_start_date: Optional[date]
    loan_monthly_payment: Optional[Decimal]
    icon: Optional[str]
    color: str
    created_at: datetime
    updated_at: datetime


class SnapshotAccountRead(SQLModel):
    """Schema for reading account snapshots."""
    id: UUID
    account_id: Optional[UUID]
    manual_account_id: Optional[UUID]
    user_id: UUID
    balance: Decimal
    snapshot_date: date
    recorded_at: datetime


class UnifiedAccountRead(SQLModel):
    """Schema for the combined list of accounts"""
    id: UUID
    name: str
    balance: Decimal
    currency: str
    source_type: str # "bank" or "manual"
    account_type: str
    # Fields below are optional because they might only exist on one side
    bank_name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    last_sync: Optional[datetime] = None
