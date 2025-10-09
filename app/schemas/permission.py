from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession



class SchemaPermissionBase(BaseModel):
    read_permission: Optional[bool] = False
    read_all_permission: Optional[bool] = False
    create_permission: Optional[bool] = False
    update_permission: Optional[bool] = False
    update_all_permission: Optional[bool] = False
    delete_permission: Optional[bool] = False
    delete_all_permission: Optional[bool] = False

    def to_permission_list(self) -> list[str]:
        """Превращает объект в список активных разрешений."""
        permissions = []
        for field_name, value in self.model_dump().items():
            if value is True:
                permissions.append(field_name)
        return permissions


class AccessContext(BaseModel):
    user_id: UUID
    permissions: List[str]


class RequestContext(BaseModel):
    session: AsyncSession
    access: AccessContext

    class Config:
        arbitrary_types_allowed = True


class SchemaUserRolesBase(BaseModel):
    user_id: UUID
    role_id: UUID
    created_at: datetime


class SchemaUserRolesCreate(BaseModel):
    user_id: UUID
    role_id: UUID


class SchemaUserRolesFilter(BaseModel):
    user_id: Optional[UUID] = None
