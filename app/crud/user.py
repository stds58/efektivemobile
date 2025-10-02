# pylint: disable=not-callable
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Role, AccessRule, BusinessElement
from app.models.user import User, user_role_association
from app.schemas.user import SchemaUserPatch, SchemaUserBase, SchemaUserFilter, UserHashPassword
from app.schemas.permission import SchemaPermissionBase
from app.crud.base import BaseDAO


class UserDAO(BaseDAO[User, SchemaUserPatch, SchemaUserFilter]):
    model = User
    create_schema = SchemaUserPatch
    filter_schema = SchemaUserFilter
    pydantic_model = SchemaUserBase

    #_exclude_from_filter_by = {"id"}

    @classmethod
    async def get_with_roles(cls, session: AsyncSession, user_id: int) -> Optional[User]:
        query = select(cls.model).where(cls.model.id == user_id).options(selectinload(cls.model.roles))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_with_permissions(
            cls,
            user_id: UUID,
            business_element_name: str,
            session: AsyncSession
    ) -> List[str]:
        query = (
            select(AccessRule)
            .join(AccessRule.element)
            .join(Role, AccessRule.role_id == Role.id)
            .join(user_role_association, Role.id == user_role_association.c.role_id)
            .where(
                user_role_association.c.user_id == user_id,
                BusinessElement.name == business_element_name
            )
        )
        result = await session.execute(query)
        access_rules = result.scalars().all()

        aggregated: SchemaPermissionBase = SchemaPermissionBase()
        for rule in access_rules:
            for field_name in aggregated.model_fields:
                if getattr(rule, field_name, False):
                    setattr(aggregated, field_name, True)

        return aggregated.to_permission_list()



class UserPasswordDAO(BaseDAO[User, None, SchemaUserFilter]):
    model = User
    create_schema = None
    filter_schema = SchemaUserFilter
    pydantic_model = UserHashPassword
