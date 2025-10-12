from typing import Optional, List
from uuid import UUID, uuid4
import structlog
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.enums import BusinessDomain
from app.core.security import get_password_hash
from app.crud.role import RoleDAO
from app.models import User
from app.crud.user import UserDAO, UserPasswordDAO
from app.schemas.base import PaginationParams
from app.schemas.role import SchemaRoleFilter
from app.schemas.permission import (
    AccessContext,
    SchemaUserRolesBase,
    SchemaUserRolesCreate,
    SchemaUserRolesFilter,
)
from app.schemas.token import Token
from app.schemas.user import (
    SchemaUserCreate,
    SchemaUserPatch,
    SchemaUserFilter,
    SchemaUserLogin,
    SchemaUserSwaggerLogin,
    SchemaUserLoginMain,
    UserHashPassword,
)
from app.services.auth_service import AuthService
from app.services.base_scoped_operations import find_many_scoped
from app.exceptions.base import (
    BadCredentialsError,
    EmailAlreadyRegisteredError,
    UserInactiveError,
    PasswordMismatchError,
    PermissionDenied,
)


logger = structlog.get_logger()


async def find_many_user(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaUserFilter,
    session: AsyncSession,
    pagination: PaginationParams,
) -> Optional[User]:
    return await find_many_scoped(
        business_element=business_element,
        methodDAO=UserDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
        owner_field="id",
    )


async def get_user_by_id(
    access: AccessContext, user_id: UUID, session: AsyncSession
) -> Optional[User]:
    filter_obj = SchemaUserFilter(id=user_id)
    user = await UserDAO.find_one(filters=filter_obj, session=session)
    if "read_all_permission" in access.permissions:
        return user
    if "read_permission" in access.permissions and user_id == access.user_id:
        return user
    logger.error("PermissionDenied")
    raise PermissionDenied(custom_detail="Missing read or read_all permission on user")


async def get_user_by_email(
    access: AccessContext, email: str, session: AsyncSession
) -> Optional[User]:
    filter_obj = SchemaUserFilter(email=email)
    user = await UserDAO.find_one(filters=filter_obj, session=session)
    if "read_all_permission" in access.permissions:
        return user
    if "read_permission" in access.permissions and user.id == access.user_id:
        return user
    logger.error("PermissionDenied")
    raise PermissionDenied(custom_detail="Missing read or read_all permission on user")


async def update_user(
    access: AccessContext,
    filters: SchemaUserPatch,
    session: AsyncSession,
    user_id: UUID,
):
    filters_dict = filters.model_dump(exclude_unset=True)
    password = filters_dict.get("password")
    if password is not None:
        password_hash = get_password_hash(password)
        filters_dict["password"] = password_hash

    if "update_all_permission" in access.permissions:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    elif "update_permission" in access.permissions and user_id == access.user_id:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
    else:
        logger.error("PermissionDenied")
        raise PermissionDenied(
            custom_detail="Missing update or update_all permission on user"
        )

    user = await get_user_by_id(access=access, user_id=user_id, session=session)
    return user


async def soft_delete_user(user_id: UUID, access: AccessContext, session: AsyncSession):
    filters_dict = {"id": user_id, "is_active": False}
    if "delete_all_permission" in access.permissions:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
        return
    if "delete_permission" in access.permissions and user_id == access.user_id:
        await UserDAO.update_one(model_id=user_id, session=session, values=filters_dict)
        return
    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing delete or delete_all permission on user"
    )


async def create_user(user_in: SchemaUserCreate, session: AsyncSession):
    fake_uuid = uuid4()
    access = AccessContext(
        user_id=fake_uuid, permissions=["read_all_permission", "create_permission"]
    )
    existing_user = await get_user_by_email(
        access=access, email=user_in.email, session=session
    )
    if existing_user:
        logger.error("EmailAlreadyRegisteredError")
        raise EmailAlreadyRegisteredError
    if user_in.password == user_in.password_confirm:
        values_dict = user_in.model_dump(exclude_unset=True)
        password_hash = get_password_hash(user_in.password)
        values_dict["password"] = password_hash
        values_dict.pop("password_confirm")
    else:
        logger.error("PasswordMismatchError")
        raise PasswordMismatchError
    user = await UserDAO.add_one(session=session, values=values_dict)

    # назначение роли user новому пользователю
    role_user = await RoleDAO.find_one(
        session=session, filters=SchemaRoleFilter(name="user")
    )
    data = SchemaUserRolesCreate(user_id=user.id, role_id=role_user.id)
    await add_role_to_user(data=data, access=access, session=session)

    return user


async def get_hash_password(
    user_id: UUID, session: AsyncSession
) -> Optional[UserHashPassword]:
    filter_obj = SchemaUserFilter(id=user_id)
    user = await UserPasswordDAO.find_one(filters=filter_obj, session=session)
    return user.password


async def get_user_roles(user_id: UUID, session: AsyncSession) -> List[str]:
    user = await UserDAO.get_with_roles(user_id=user_id, session=session)
    if user is None:
        return []
    return [role.name for role in user.roles]


async def set_token_in_cookie(response: Response, tokens: Token):
    response.set_cookie(
        key="users_access_token",
        value=tokens.access_token,
        httponly=True,
        secure=False,
        domain=None,
        path="/",
        samesite="strict",
        max_age=60 * settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    response.set_cookie(
        key="users_refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,  # settings.SECURE_COOKIES
        domain=None,
        path="/",
        samesite="strict",
        max_age=60 * 60 * settings.REFRESH_TOKEN_EXPIRE_HOURS,
    )
    return


async def authenticate_user(
    user_in: SchemaUserLoginMain, session: AsyncSession
) -> Token:
    login = user_in.email if user_in.username is None else user_in.username
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_email(access=access, email=login, session=session)

    if not user:
        logger.error("в БД отсутствует user_id", user_id=user.id)
        raise BadCredentialsError
    if not user.is_active:
        logger.error("пользователь отключён", user_id=user.id)
        raise UserInactiveError
    hash_password = await get_hash_password(user_id=user.id, session=session)
    if not AuthService.verify_password(user_in.password, hash_password):
        raise BadCredentialsError

    role_names = await get_user_roles(user_id=user.id, session=session)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": role_names}
    )
    refresh_token = AuthService.create_refresh_token({"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


async def authenticate_user_api(
    user_in: SchemaUserLogin, session: AsyncSession
) -> Token:
    user = SchemaUserLoginMain(email=user_in.email, password=user_in.password)
    return await authenticate_user(user_in=user, session=session)


async def authenticate_user_swagger(
    user_in: SchemaUserSwaggerLogin, session: AsyncSession
) -> Token:
    user = SchemaUserSwaggerLogin(username=user_in.username, password=user_in.password)
    return await authenticate_user(user_in=user, session=session)


async def refresh_user_tokens(refresh_token: str, session: AsyncSession) -> Token:
    payload = AuthService.decode_refresh_token(refresh_token)
    user_id = payload.get("sub")
    if not user_id:
        logger.error("BadCredentialsError")
        raise BadCredentialsError

    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_id(access=access, user_id=UUID(user_id), session=session)

    if not user:
        logger.error("BadCredentialsError")
        raise BadCredentialsError
    if not user.is_active:
        logger.error("UserInactiveError")
        raise UserInactiveError

    new_access = AuthService.create_access_token({"sub": str(user.id)})
    new_refresh = AuthService.create_refresh_token({"sub": str(user.id)})

    AuthService.ban_token(refresh_token)

    return Token(access_token=new_access, refresh_token=new_refresh)


async def add_role_to_user(
    data: SchemaUserRolesCreate, access: AccessContext, session: AsyncSession
) -> SchemaUserRolesBase:
    if "create_permission" in access.permissions:
        return await UserDAO.add_role_to_user(
            session=session, user_id=data.user_id, role_id=data.role_id
        )
    logger.error("PermissionDenied")
    raise PermissionDenied(custom_detail="Missing create_permission on user_roles")


async def remove_role_from_user(
    data: SchemaUserRolesCreate, access: AccessContext, session: AsyncSession
) -> dict:
    if "delete_all_permission" in access.permissions:
        return await UserDAO.remove_role_from_user(
            session=session, user_id=data.user_id, role_id=data.role_id
        )

    if "delete_permission" in access.permissions:
        if access.user_id == data.user_id:
            return await UserDAO.remove_role_from_user(
                session=session, user_id=data.user_id, role_id=data.role_id
            )
        logger.error("PermissionDenied")
        raise PermissionDenied(
            custom_detail="Missing delete or delete_all permission on user_roles"
        )

    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing delete or delete_all permission on user_roles"
    )


async def get_all_user_roles(
    filters: SchemaUserRolesFilter, access: AccessContext, session: AsyncSession
) -> List[dict]:
    if "read_all_permission" in access.permissions:
        return await UserDAO.get_from_user_roles(
            session=session, user_id=filters.user_id
        )

    if "read_permission" in access.permissions:
        if filters.user_id is not None and filters.user_id != access.user_id:
            logger.error("PermissionDenied")
            raise PermissionDenied(
                custom_detail="Missing read or read_all permission on user_roles"
            )
        filters.user_id = access.user_id
        return UserDAO.get_from_user_roles(session=session, user_id=filters.user_id)

    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing read or read_all permission on user_roles"
    )


async def ensure_user_is_active(user_id: UUID, session: AsyncSession) -> bool:
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_id(access=access, user_id=user_id, session=session)
    if user is None:
        raise BadCredentialsError
    if not user.is_active:
        raise UserInactiveError
    return True
