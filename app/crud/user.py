# pylint: disable=not-callable
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import Role
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.user import SchemaUserCreate, SchemaUserPatch
from app.crud.base import CRUDBase


class CRUDUser(CRUDBase[User]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_roles(self, db: AsyncSession, *, user_id: int) -> List[Role]:
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        return user.roles if user else []

    async def create(self, db: AsyncSession, *, obj_in: SchemaUserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=True,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: SchemaUserPatch
    ) -> User:
        update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data.pop("password"))
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, db: AsyncSession, *, obj_id: str) -> bool:
        db_user = await self.get(db, obj_id)
        if not db_user:
            return False
        db_user.is_active = False
        db.add(db_user)
        await db.commit()
        return True



# Экземпляр для использования в сервисах
user = CRUDUser(User)
