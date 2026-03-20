from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class SavingsGoal(SQLModel, table=True):
    __tablename__ = "savings_goals"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    name: str
    target_amount: Optional[Decimal] = Field(
        default=None, max_digits=12, decimal_places=2
    )
    current_amount: Decimal = Field(default=0.00, max_digits=12, decimal_places=2)
    icon: Optional[str] = Field(default="BanknotesIcon", max_length=100)
    color: str = Field(default="#3b82f6", max_length=7)
    
    automation_amount: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    automation_frequency: Optional[str] = Field(default=None, max_length=50)  # 'monthly', 'quarterly', etc.
    automation_next_run_date: Optional[date] = Field(default=None)
    automation_is_active: bool = Field(default=False)

    transactions: List["Transaction"] = Relationship(back_populates="saving_goal")

class SavingsGoalRead(SQLModel):
    id: UUID
    name: str
    target_amount: Optional[Decimal]
    current_amount: Decimal
    icon: Optional[str]
    color: str
    automation_amount: Optional[Decimal]
    automation_frequency: Optional[str]
    automation_next_run_date: Optional[date]
    automation_is_active: bool