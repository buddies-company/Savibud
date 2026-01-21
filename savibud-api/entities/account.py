from datetime import datetime
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
    bank_name: str
    account_type: str  # e.g., "checking", "savings"
    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="EUR")
    last_sync: Optional[datetime] = None
    is_active: bool = Field(default=True)
    raw_data: Optional[dict] = Field(default={}, sa_type=JSONB)

class SnapshotAccount(SQLModel, table=True):
    
    __tablename__ = "snapshot_accounts"
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(foreign_key="accounts.id")
    balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    snapshot_date: datetime = Field(default=datetime.today())
