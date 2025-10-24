from app.crud.base import BaseDAO
from app.models.user_role import UserRole
from app.schemas.user_role import (
    SchemaUserRoleBase,
    SchemaUserRoleCreate,
    SchemaUserRoleFilter,
)


class UserRoleDAO(BaseDAO[UserRole, SchemaUserRoleCreate, SchemaUserRoleFilter]):
    model = UserRole
    create_schema = SchemaUserRoleCreate
    filter_schema = SchemaUserRoleFilter
    pydantic_model = SchemaUserRoleBase
