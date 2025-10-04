from typing import Optional, Annotated
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class SchemaOrderBase(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    quantity: int
    is_paid: bool
    created_at: datetime
    updated_at: datetime


class SchemaOrderCreate(BaseModel):
    product_id: UUID
    quantity: Annotated[int, Field(gt=0)]
    is_paid: bool = False


class SchemaOrderFilter(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    quantity: Optional[int] = None
    is_paid: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SchemaOrderPatch(BaseModel):
    quantity: Optional[int] = None
    is_paid: Optional[bool] = None
