from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class PowensConnection(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    powens_access_token: str


class PowensCred(BaseModel):
    code: str
    user_id: str
