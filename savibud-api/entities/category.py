from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class BudgetPeriod(str, Enum):
    """Budget period enum"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


class Category(SQLModel, table=True):
    """Category definition with integrated budget properties"""

    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    name: str
    parent_id: Optional[UUID] = Field(default=None, foreign_key="categories.id")
    icon: Optional[str] = None
    color: Optional[str] = None
    is_income: bool = Field(default=False)
    
    budget_amount: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    budget_period: Optional[BudgetPeriod] = Field(default=BudgetPeriod.monthly)
    budget_start_date: Optional[date] = Field(default=None)
    budget_end_date: Optional[date] = Field(default=None)
    is_fixed: bool = Field(default=False)  # TRUE for "Rent", FALSE for "Groceries"

    transactions: list["Transaction"] = Relationship(back_populates="category")


class CategoryRead(SQLModel):
    id: UUID
    name: str
    icon: Optional[str]
    color: Optional[str]
    parent_id: Optional[UUID]
    is_income: bool
    budget_amount: Optional[Decimal] = None
    budget_period: BudgetPeriod = BudgetPeriod.monthly
    is_fixed: bool = False
