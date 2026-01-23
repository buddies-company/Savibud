from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship


class Category(SQLModel, table=True):
    """Category definition"""

    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    parent_id: Optional[UUID] = Field(default=None, foreign_key="categories.id")
    icon: Optional[str] = None
    color: Optional[str] = None
    is_income: bool = Field(default=False)
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    
    budgets: list["Budget"] = Relationship(back_populates="category")

class CategoryRead(SQLModel):
    id: UUID
    name: str
    icon: Optional[str]
    color: Optional[str]
    parent_id: Optional[UUID]
    is_income: bool
