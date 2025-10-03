from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SchemaAccessRuleBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    role_id: UUID
    businesselement_id: UUID
    read_permission: bool
    read_all_permission: bool
    create_permission: bool
    update_permission: bool
    update_all_permission: bool
    delete_permission: bool
    delete_all_permission: bool


class SchemaAccessRuleFilter(BaseModel):
    id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    businesselement_id: Optional[UUID] = None
    read_permission: Optional[bool] = False
    read_all_permission: Optional[bool] = False
    create_permission: Optional[bool] = False
    update_permission: Optional[bool] = False
    update_all_permission: Optional[bool] = False
    delete_permission: Optional[bool] = False
    delete_all_permission: Optional[bool] = False


class SchemaAccessRulePatch(BaseModel):
    read_permission: Optional[bool] = False
    read_all_permission: Optional[bool] = False
    create_permission: Optional[bool] = False
    update_permission: Optional[bool] = False
    update_all_permission: Optional[bool] = False
    delete_permission: Optional[bool] = False
    delete_all_permission: Optional[bool] = False
