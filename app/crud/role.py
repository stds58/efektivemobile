from app.crud.base import BaseDAO
from app.models.role import Role
from app.schemas.role import SchemaRoleBase, SchemaRoleFilter


class RoleDAO(BaseDAO[Role, None, SchemaRoleFilter]):
    model = Role
    create_schema = None
    filter_schema = SchemaRoleFilter
    pydantic_model = SchemaRoleBase
