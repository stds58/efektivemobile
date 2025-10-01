from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import SchemaUserCreate, SchemaUserPatch, UserPublic, SchemaUserFilter
from app.schemas.permission import SchemaPermissionBase
from app.services.auth_service import AuthService
from app.crud.user import user as crud_user
from app.exceptions.base import (
    BadCredentialsError,
    EmailAlreadyRegisteredError,
    UserInactiveError,
)
from app.models import Role, BusinessElement, AccessRule, User
from uuid import UUID
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied
from app.crud.user import UserDAO
from app.schemas.base import PaginationParams
from app.core.security import get_password_hash


async def find_many_user(
        access: AccessContext,
        filters: SchemaUserFilter,
        session: AsyncSession,
        pagination: PaginationParams
):
    if "read_all_permission" in access.permissions:
        users = await UserDAO.find_many(filters=filters, session=session, pagination=pagination)
    elif "read_permission" in access.permissions:
        filters.id = access.user_id
        users = await UserDAO.find_many(filters=filters, session=session, pagination=pagination)
    else:
        raise PermissionDenied(custom_detail="Missing read or read_all permission on user")
    return users


async def update_user(
        filters: SchemaUserPatch,
        session: AsyncSession,
        user_id: UUID
):
    filters_dict = filters.model_dump(exclude_unset=True)
    password = filters_dict.get("password")
    password_hash = get_password_hash(password)
    filters_dict["password"] = password_hash
    await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    filter_obj = SchemaUserFilter(id=user_id)
    user = await UserDAO.find_one(filters=filter_obj, session=session)
    return user



class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await crud_user.get_by_email(self.db, email=email)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        return await crud_user.get(self.db, obj_id=user_id)

    async def create_user(self, user_in: SchemaUserCreate) -> UserPublic:
        existing_user = await self.get_user_by_email(user_in.email)
        if existing_user:
            raise EmailAlreadyRegisteredError
        user = await crud_user.create(self.db, obj_in=user_in)
        return UserPublic.model_validate(user, from_attributes=True)

    async def get_user_roles(self, user_id: str) -> Optional[User]:
        return await crud_user.get_user_roles(self.db, user_id=user_id)

    async def update_user(
        self, user_id: str, user_in: SchemaUserPatch
    ) -> Optional[UserPublic]:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise BadCredentialsError
        updated_user = await crud_user.update(self.db, db_obj=user, obj_in=user_in)
        return UserPublic.model_validate(updated_user, from_attributes=True)

    async def soft_delete_user(self, user_id: str) -> bool:
        return await crud_user.soft_delete(self.db, obj_id=user_id)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user:
            raise BadCredentialsError
        if not user.is_active:
            raise UserInactiveError
        if not AuthService.verify_password(password, user.password):
            raise BadCredentialsError
        return user

    async def check_permission(
            self,
            user_id: int,
            business_element_name: str,
            permission: str
    ) -> bool:
        # Получаем все роли пользователя
        roles = await self.get_user_roles(user_id=user_id)
        role_names = [role.name for role in roles]

        if not role_names:
            return False

        # Запрос: есть ли хоть одно правило с нужным разрешением = True?
        result = await self.db.execute(
            select(AccessRule)
            .join(Role)
            .join(BusinessElement)
            .where(
                Role.name.in_(role_names),
                BusinessElement.name == business_element_name,
                getattr(AccessRule, permission) == True
            )
        )
        return result.first() is not None

    async def get_user_permission(
            self,
            user_id: UUID,
            business_element_name: str
    ) -> List[str]:
        # Получаем все роли пользователя
        roles = await self.get_user_roles(user_id=user_id)
        role_names = [role.name for role in roles]

        if not role_names:
            return []

        # Запрос: есть ли хоть одно правило с нужным разрешением = True?
        result = await self.db.execute(
            select(AccessRule)
            .join(Role)
            .join(BusinessElement)
            .where(
                Role.name.in_(role_names),
                BusinessElement.name == business_element_name
            )
        )
        # Получаем правила из БД
        access_rules = result.scalars().all()

        # Создаём "суммарный" объект прав
        aggregated = SchemaPermissionBase()

        for rule in access_rules:
            # Для каждого поля: если в правиле True — ставим True в агрегированном
            for field_name in aggregated.model_fields:
                if getattr(rule, field_name, False):
                    setattr(aggregated, field_name, True)
        return aggregated.to_permission_list()


