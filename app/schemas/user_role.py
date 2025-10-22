from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaUserRoleBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: UUID
    role_id: UUID


class SchemaUserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID


class SchemaUserRoleFilter(BaseModel):
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
