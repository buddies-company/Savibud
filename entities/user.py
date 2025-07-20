from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    """JWT structure"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Jwt payload data"""

    username: str | None = None
    user_id: int | None = None


class User(BaseModel):
    """User definition"""

    id: Union[int, None] = None
    username: str
    password: str

    def __init__(self, username: str, password: str, user_id: int = None) -> None:
        super().__init__(username=username, password=password, id=user_id)
