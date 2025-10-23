from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaBusinessElementBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    description: str


class SchemaBusinessElementFilter(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
