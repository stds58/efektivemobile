from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: UUID


class AccessToken(BaseModel):
    sub: UUID
    role: List[str]
    exp: int
    iat: int


class RefreshToken(BaseModel):
    sub: UUID
    exp: int
    iat: int
    type: str = "refresh"
