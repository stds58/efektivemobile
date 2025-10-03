from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaOrderBase(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    is_paid: bool
    created_at: datetime
    updated_at: datetime


class SchemaOrderCreate(BaseModel):
    user_id: UUID
    product_id: UUID
    is_paid: bool


class SchemaOrderFilter(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID = None
    product_id: UUID
    is_paid: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SchemaOrderPatch(BaseModel):
    is_paid: Optional[bool] = None
