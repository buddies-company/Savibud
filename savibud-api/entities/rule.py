"""Categorization rules for automatic transaction categorization."""

from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Rule(SQLModel, table=True):
    """Rule for automatically categorizing transactions or assigning to savings goals."""

    __tablename__ = "rules"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    category_id: Optional[UUID] = Field(default=None, foreign_key="categories.id")
    savings_goal_id: Optional[UUID] = Field(default=None, foreign_key="savings_goals.id")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Matching conditions (at least one must match)
    keywords: Optional[List[str]] = Field(
        default=None, 
        sa_column=Column(ARRAY(Text))
    )
    regex_pattern: Optional[str] = Field(default=None, max_length=255)  # e.g., ".*grocery.*"
    min_amount: Optional[float] = Field(default=None)
    max_amount: Optional[float] = Field(default=None)
    
    is_active: bool = Field(default=True)
    priority: int = Field(default=100)  # Higher priority rules applied first


class RuleRead(SQLModel):
    """Read model for Rule."""

    id: UUID
    category_id: Optional[UUID]
    savings_goal_id: Optional[UUID]
    name: str
    description: Optional[str]
    keywords: Optional[list[str]]
    regex_pattern: Optional[str]
    min_amount: Optional[float]
    max_amount: Optional[float]
    is_active: bool
    priority: int
