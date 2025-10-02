from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models import User
from app.crud.user import UserDAO, UserPasswordDAO
from app.schemas.base import PaginationParams
from app.schemas.permission import AccessContext
from app.schemas.token import Token
from app.schemas.user import (
    SchemaUserCreate,
    SchemaUserPatch,
    SchemaUserFilter,
    SchemaUserLogin,
    UserHashPassword
)
from app.services.auth_service import AuthService
from app.exceptions.base import (
    BadCredentialsError,
    EmailAlreadyRegisteredError,
    UserInactiveError,
    PasswordMismatchError,
    PermissionDenied,
)


async def find_many_user(
        access: AccessContext,
        filters: SchemaUserFilter,
        session: AsyncSession,
        pagination: PaginationParams
) -> Optional[User]:
    if "read_all_permission" in access.permissions:
        users = await UserDAO.find_many(filters=filters, session=session, pagination=pagination)
    elif "read_permission" in access.permissions:
        if filters.id is not None and filters.id != access.user_id:
            raise PermissionDenied(custom_detail="Missing read or read_all permission on user")
        filters.id = access.user_id
        users = await UserDAO.find_many(filters=filters, session=session, pagination=pagination)
    else:
        raise PermissionDenied(custom_detail="Missing read or read_all permission on user")
    return users


async def get_user_by_id(access: AccessContext, user_id: UUID, session: AsyncSession) -> Optional[User]:
    filter_obj = SchemaUserFilter(id=user_id)
    if "read_all_permission" in access.permissions:
        user = await UserDAO.find_one(filters=filter_obj, session=session)
    elif "read_permission" in access.permissions and user_id == access.user_id:
        user = await UserDAO.find_one(filters=filter_obj, session=session)
    else:
        raise PermissionDenied(custom_detail="Missing read or read_all permission on user")
    return user


async def get_user_by_email(access: AccessContext, email: str, session: AsyncSession) -> Optional[User]:
    filter_obj = SchemaUserFilter(email=email)
    user = await UserDAO.find_one(filters=filter_obj, session=session)
    if "read_all_permission" in access.permissions:
        return user
    if "read_permission" in access.permissions and user.id == access.user_id:
        return user
    raise PermissionDenied(custom_detail="Missing read or read_all permission on user")


async def update_user(
        access: AccessContext,
        filters: SchemaUserPatch,
        session: AsyncSession,
        user_id: UUID
):
    filters_dict = filters.model_dump(exclude_unset=True)
    password = filters_dict.get("password")
    password_hash = get_password_hash(password)
    filters_dict["password"] = password_hash

    if "update_all_permission" in access.permissions:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    elif "update_permission" in access.permissions and user_id == access.user_id:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    else:
        raise PermissionDenied(custom_detail="Missing update or update_all permission on user")

    user = await get_user_by_id(access=access, user_id=user_id, session=session)
    return user


async def soft_delete_user(
        user_id: UUID,
        access: AccessContext,
        session: AsyncSession
):
    filters_dict = {"id": user_id, "is_active": False}
    if "delete_all_permission" in access.permissions:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    elif "delete_permission" in access.permissions and user_id == access.user_id:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    else:
        raise PermissionDenied(custom_detail="Missing delete or delete_all permission on user")

    return


async def create_user(user_in: SchemaUserCreate,session: AsyncSession):
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid,permissions=["read_all_permission"])
    existing_user = await get_user_by_email(access=access, email=user_in.email, session=session)
    if existing_user:
        raise EmailAlreadyRegisteredError
    if user_in.password == user_in.password_confirm:
        values_dict = user_in.model_dump(exclude_unset=True)
        password_hash = get_password_hash(user_in.password)
        values_dict["password"] = password_hash
        values_dict.pop("password_confirm")
    else:
        raise PasswordMismatchError
    user = await UserDAO.add_one(session=session, values=values_dict)
    return user


async def get_hash_password(user_id: UUID, session: AsyncSession) -> Optional[UserHashPassword]:
    filter_obj = SchemaUserFilter(id=user_id)
    user = await UserPasswordDAO.find_one(filters=filter_obj, session=session)
    return user.password


async def get_user_roles(user_id: UUID, session: AsyncSession) -> List[str]:
    user = await UserDAO.get_with_roles(user_id=user_id, session=session)
    if user is None:
        return []
    return [role.name for role in user.roles]


async def authenticate_user(user_in:SchemaUserLogin, session: AsyncSession) -> Token:
    login = user_in.email if user_in.username is None else user_in.username
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])

    user = await get_user_by_email(access=access, email=login, session=session)

    if not user:
        raise BadCredentialsError
    if not user.is_active:
        raise UserInactiveError
    hash_password = await get_hash_password(user_id=user.id, session=session)
    if not AuthService.verify_password(user_in.password, hash_password):
        raise BadCredentialsError

    role_names = await get_user_roles(user_id=user.id, session=session)
    access_token = AuthService.create_access_token(data={"sub": str(user.id), "role": role_names})

    return Token(access_token=access_token, token_type="bearer")
