from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.user import SchemaUserBase, SchemaUserFilter
from app.crud.base_m2m import M2MDAO


class UserRolesDAO(M2MDAO[User, UserRole, Role, SchemaUserBase, SchemaUserFilter]):
    source_model = User
    through_model = UserRole
    target_model = Role
    source_schema = SchemaUserBase
    filter_schema = SchemaUserFilter
    target_attr_name = "roles"
