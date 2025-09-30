from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import SchemaUserCreate, SchemaUserPatch, UserPublic
from app.services.auth_service import AuthService
from app.crud.user import user as crud_user
from app.exceptions.base import (
    BadCredentialsError,
    EmailAlreadyRegisteredError,
    UserInactiveError,
)
from app.models import Role, BusinessElement, AccessRule, User



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
            permission: str  # например, "update_permission"
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


