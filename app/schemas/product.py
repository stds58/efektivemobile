from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaProductBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: UUID
    name: str
    price: int


class SchemaProductCreate(BaseModel):
    user_id: UUID
    name: str
    price: int


class SchemaProductFilter(BaseModel):
    name: Optional[str] = None
    user_id: Optional[UUID] = None
    price: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# class SchemaProductFilterSystem(SchemaProductFilter):
#     user_id: Optional[UUID] = None
