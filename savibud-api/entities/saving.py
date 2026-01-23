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

    automations: List["SavingsAutomation"] = Relationship(back_populates="goal")


class SavingsAutomation(SQLModel, table=True):
    __tablename__ = "savings_automations"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    goal_id: UUID = Field(foreign_key="savings_goals.id")
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    frequency: str  # 'monthly', 'quarterly', etc.
    next_run_date: date
    is_active: bool = Field(default=True)

    goal: SavingsGoal = Relationship(back_populates="automations")
