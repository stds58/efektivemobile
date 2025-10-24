from app.models.user import User
from app.schemas.user import (
    SchemaUserPatch,
    SchemaUserBase,
    SchemaUserFilter,
    UserHashPassword,
)
from app.crud.base import BaseDAO


class UserDAO(BaseDAO[User, SchemaUserPatch, SchemaUserFilter]):
    model = User
    create_schema = SchemaUserPatch
    filter_schema = SchemaUserFilter
    pydantic_model = SchemaUserBase

    # _exclude_from_filter_by = {"id"}

    # @classmethod
    # async def get_with_permissions(
    #     cls, user_id: UUID, business_element_name: str, session: AsyncSession
    # ) -> List[str]:
    #     pass
    # query = (
    #     select(AccessRule)
    #     .join(AccessRule.element)
    #     .join(Role, AccessRule.role_id == Role.id)
    #     .join(user_role_association, Role.id == user_role_association.c.role_id)
    #     .where(
    #         user_role_association.c.user_id == user_id,
    #         BusinessElement.name == business_element_name,
    #     )
    # )
    # result = await session.execute(query)
    # access_rules = result.scalars().all()
    #
    # aggregated: SchemaPermissionBase = SchemaPermissionBase()
    # for rule in access_rules:
    #     for field_name in aggregated.model_fields:
    #         if getattr(rule, field_name, False):
    #             setattr(aggregated, field_name, True)
    #
    # return aggregated.to_permission_list()


class UserPasswordDAO(BaseDAO[User, None, SchemaUserFilter]):
    model = User
    create_schema = None
    filter_schema = SchemaUserFilter
    pydantic_model = UserHashPassword
