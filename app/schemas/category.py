from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaCategoryBase(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class SchemaCategoryCreate(BaseModel):
    name: str


class SchemaCategoryFilter(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SchemaCategoryPatch(BaseModel):
    name: Optional[str] = None
