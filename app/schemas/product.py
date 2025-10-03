from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaProductBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    category_id: UUID
    name: str
    price: int


class SchemaProductCreate(BaseModel):
    category_id: UUID
    name: str
    price: int


class SchemaProductFilter(BaseModel):
    category_id: UUID
    name: Optional[str] = None
    price: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SchemaProductPatch(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    price: Optional[int] = None
