from datetime import date as date_type
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from entities.category import CategoryRead


class Transaction(SQLModel, table=True):    
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: Optional[UUID] = Field(default=None, foreign_key="accounts.id")
    category_id: Optional[UUID] = Field(default=None, foreign_key="categories.id")
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id", index=True)
    powens_transaction_id: Optional[str] = Field(
        default=None, index=True, nullable=False, unique=True
    )
    amount: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    label: str
    date: date_type = Field(default_factory=date_type.today)
    raw_data: Optional[dict] = Field(default={}, sa_type=JSONB)
    is_deleted: bool = Field(default=False)
    savings_goal_id: Optional["UUID"] = Field(
        default=None, foreign_key="savings_goals.id"
    )
    is_internal: bool = Field(default=False)
    internal_link_id: Optional[int] = Field(default=None, foreign_key="transactions.id")
    

class TransactionReadWithCategory(SQLModel):
    id: Optional[int]
    account_id: Optional[UUID]
    category_id: Optional[UUID]
    amount: Decimal
    label: str
    date: date_type
    is_deleted: bool
    savings_goal_id: Optional["UUID"]
    is_internal: bool
    category: Optional[CategoryRead] = None