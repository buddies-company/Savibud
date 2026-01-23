from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from entities.category import CategoryRead


class BudgetPeriod(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


class Budget(SQLModel, table=True):
    """Budget definition"""

    __tablename__ = "budgets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    category_id: UUID = Field(foreign_key="categories.id")
    amount: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    period: BudgetPeriod = Field(default=BudgetPeriod.monthly)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    is_fixed: bool = Field(default=False)  # TRUE for "Rent", FALSE for "Groceries"

    category: Optional["Category"] = Relationship(back_populates="budgets")

class BudgetReadWithCategory(SQLModel):
    id: UUID
    amount: Decimal
    period: BudgetPeriod
    category_id: UUID
    is_fixed: bool
    # This is the key: we include the CategoryRead schema here
    category: Optional[CategoryRead] = None