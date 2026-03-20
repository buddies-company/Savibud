from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Token(BaseModel):
    """JWT structure"""

    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    """Jwt payload data"""

    username: str | None = None
    user_id: UUID | None = None
    database: str | None = None


class User(SQLModel, table=True):
    """User definition"""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    password: str
