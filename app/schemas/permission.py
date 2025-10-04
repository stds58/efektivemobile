from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


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
