# pylint: disable=not-callable
from typing import Optional, List
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert
from sqlalchemy.orm import selectinload
from app.models import Role, AccessRule, BusinessElement
from app.models.user import User #, user_role_association
from app.schemas.user import (
    SchemaUserPatch,
    SchemaUserBase,
    SchemaUserFilter,
    UserHashPassword,
)
from app.schemas.permission import SchemaPermissionBase, SchemaUserRolesBase
from app.crud.base import BaseDAO
from app.exceptions.base import ObjectsNotFoundByIDError, IntegrityErrorException


class UserDAO(BaseDAO[User, SchemaUserPatch, SchemaUserFilter]):
    model = User
    create_schema = SchemaUserPatch
    filter_schema = SchemaUserFilter
    pydantic_model = SchemaUserBase

    # _exclude_from_filter_by = {"id"}

    # @classmethod
    # async def get_with_roles(
    #     cls, session: AsyncSession, user_id: UUID
    # ) -> Optional[User]:
    #     query = (
    #         select(cls.model)
    #         .where(cls.model.id == user_id)
    #         .options(selectinload(cls.model.roles))
    #     )
    #     result = await session.execute(query)
    #     return result.scalar_one_or_none()

    @classmethod
    async def get_with_permissions(
        cls, user_id: UUID, business_element_name: str, session: AsyncSession
    ) -> List[str]:
        pass
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

    @classmethod
    async def add_role_to_user(
        cls, session: AsyncSession, user_id: UUID, role_id: UUID
    ) -> SchemaUserRolesBase:
        pass
        # user = await session.get(User, user_id)
        # role = await session.get(Role, role_id)
        # if not user:
        #     raise ObjectsNotFoundByIDError("Пользователь не найден")
        # if not role:
        #     raise ObjectsNotFoundByIDError("Роль не найдена")
        #
        # try:
        #     stmt = (
        #         insert(user_role_association)
        #         .values(user_id=user_id, role_id=role_id)
        #         .returning(user_role_association.c.created_at)
        #     )
        #     result = await session.execute(stmt)
        #     created_at = result.scalar_one()
        # except IntegrityError as exc:
        #     await session.rollback()
        #     raise IntegrityErrorException from exc
        #
        # await session.commit()
        #
        # return SchemaUserRolesBase(
        #     user_id=user_id,
        #     role_id=role_id,
        #     created_at=created_at,
        # )

    @classmethod
    async def remove_role_from_user(
        cls,
        session: AsyncSession,
        user_id: UUID,
        role_id: UUID,
    ) -> dict:
        pass
        # user = await session.get(User, user_id)
        # role = await session.get(Role, role_id)
        # if not user:
        #     raise ObjectsNotFoundByIDError("Пользователь не найден")
        # if not role:
        #     raise ObjectsNotFoundByIDError("Роль не найдена")
        #
        # stmt = delete(user_role_association).where(
        #     user_role_association.c.user_id == user_id,
        #     user_role_association.c.role_id == role_id,
        # )
        # result = await session.execute(stmt)
        # await session.commit()
        #
        # if result.rowcount == 0:
        #     raise ObjectsNotFoundByIDError("Такая роль у пользователя не обнаружена")
        # return {"message": "Роль удалена"}

    @classmethod
    async def get_from_user_roles(
        cls, session: AsyncSession, user_id: Optional[UUID] = None
    ) -> List[dict]:
        pass
        # query = select(
        #     user_role_association.c.user_id,
        #     user_role_association.c.role_id,
        #     user_role_association.c.created_at,
        #     User.email,
        #     Role.name.label("role_name"),
        # ).select_from(
        #     user_role_association.join(
        #         User, User.id == user_role_association.c.user_id
        #     ).join(Role, Role.id == user_role_association.c.role_id)
        # )
        #
        # if user_id is not None:
        #     query = query.where(user_role_association.c.user_id == user_id)
        #
        # result = await session.execute(query)
        # rows = result.fetchall()
        #
        # return [
        #     {
        #         "user_id": row.user_id,
        #         "user_email": row.email,
        #         "role_id": row.role_id,
        #         "role_name": row.role_name,
        #         "created_at": row.created_at,
        #     }
        #     for row in rows
        # ]


class UserPasswordDAO(BaseDAO[User, None, SchemaUserFilter]):
    model = User
    create_schema = None
    filter_schema = SchemaUserFilter
    pydantic_model = UserHashPassword
