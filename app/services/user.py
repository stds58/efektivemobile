from typing import Optional, List
from uuid import UUID
from secrets import compare_digest
import structlog
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.enums import BusinessDomain
from app.core.stubs import FAKE_ACCESS_CONTEXT
from app.models import User
from app.crud.role import RoleDAO
from app.crud.user import UserDAO, UserPasswordDAO
from app.crud.user_role import UserRoleDAO
from app.schemas.base import PaginationParams
from app.schemas.role import SchemaRoleFilter
from app.schemas.permission import (
    AccessContext,
    SchemaUserRolesBase,
    SchemaUserRolesCreate,
    SchemaUserRolesFilter,
)
from app.schemas.token import Token, AccessToken, RefreshToken
from app.schemas.user import (
    SchemaUserCreate,
    SchemaUserPatch,
    SchemaUserFilter,
    SchemaUserLogin,
    SchemaUserSwaggerLogin,
    SchemaUserLoginMain,
    UserHashPassword,
    SchemaChangePasswordRequest,
    SchemaUserPasswordUpdate,
)
from app.services.base_scoped_operations import find_many_scoped
from app.services.user_role import find_one_user_role, find_many_user_role, get_list_user_rolenames
from app.services.auth.tokens import create_access_token, create_refresh_token, decode_refresh_token
from app.services.auth.password import verify_password, get_password_hash
from app.services.auth.blacklist import token_blacklist
from app.services.base import (
    find_one_business_element,
    find_many_business_element,
    add_one_business_element,
    update_one_business_element,
    delete_one_business_element,
)
from app.exceptions.base import (
    BadCredentialsError,
    EmailAlreadyRegisteredError,
    UserInactiveError,
    PasswordMismatchError,
    PermissionDenied,
    InvalidTokenError,
)
from app.services.user_role import get_list_user_rolenames


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
    filters = SchemaUserFilter(id=user_id)
    user = await find_one_business_element(
        business_element=BusinessDomain.USER,
        methodDAO=UserDAO,
        access=access,
        filters=filters,
        session=session,
    )
    return user


async def get_user_by_email(
    access: AccessContext, email: str, session: AsyncSession
) -> Optional[User]:
    filters = SchemaUserFilter(email=email)
    user = await find_one_business_element(
        business_element=BusinessDomain.USER,
        methodDAO=UserDAO,
        access=access,
        filters=filters,
        session=session,
    )
    return user


async def update_user(
    access: AccessContext,
    filters: SchemaUserPatch,
    session: AsyncSession,
    user_id: UUID,
):
    return await update_one_business_element(
        business_element=BusinessDomain.USER,
        methodDAO=UserDAO,
        access=access,
        data=filters,
        session=session,
        business_element_id=user_id,
    )


async def user_change_password(
    access: AccessContext,
    filters: SchemaChangePasswordRequest,
    session: AsyncSession,
    user_id: UUID,
):
    # compare_digest - предназначен для безопасного сравнения секретов (паролей, токенов, хешей).
    # Работает за фиксированное время, независимо от того, где отличие
    if not compare_digest(filters.new_password, filters.new_password_confirm):
        raise BadCredentialsError

    hash_old_password = await get_hash_password(user_id=user_id, session=session)
    if not await verify_password(filters.old_password, hash_old_password):
        raise BadCredentialsError

    data = SchemaUserPasswordUpdate(
        password=get_password_hash(filters.new_password)
    )
    return await update_one_business_element(
        business_element=BusinessDomain.USER,
        methodDAO=UserDAO,
        access=access,
        data=data,
        session=session,
        business_element_id=user_id,
    )


async def soft_delete_user(
    user_id: UUID, access: AccessContext, session: AsyncSession
):
    filters = SchemaUserFilter(id=user_id, is_active=False)
    return await update_one_business_element(
        business_element=BusinessDomain.USER,
        methodDAO=UserDAO,
        access=access,
        data=filters,
        session=session,
        business_element_id=user_id,
    )


async def create_user(user_in: SchemaUserCreate, session: AsyncSession):
    existing_user = await get_user_by_email(
        access=FAKE_ACCESS_CONTEXT, email=user_in.email, session=session
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
    await add_role_to_user(data=data, access=FAKE_ACCESS_CONTEXT, session=session)

    return user


async def get_hash_password(
    user_id: UUID, session: AsyncSession
) -> Optional[UserHashPassword]:
    filter_obj = SchemaUserFilter(id=user_id)
    user = await UserPasswordDAO.find_one(filters=filter_obj, session=session)
    return user.password


async def set_access_token_in_cookie(response: Response, access_token: AccessToken):
    try:
        response.delete_cookie("access_token")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            domain=None,
            path="/",
            samesite="strict",
            max_age=60 * settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        return {
            "status": "success",
            "access_expires_in": 60 * settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
    except Exception:
        response.delete_cookie("access_token")
        raise InvalidTokenError


async def set_refresh_token_in_cookie(response: Response, refresh_token: RefreshToken):
    try:
        response.delete_cookie("refresh_token")
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # settings.SECURE_COOKIES
            domain=None,
            path="/",
            samesite="strict",
            max_age=60 * 60 * settings.REFRESH_TOKEN_EXPIRE_HOURS,
        )
        return {
            "status": "success",
            "refresh_expires_in": 60 * 60 * settings.REFRESH_TOKEN_EXPIRE_HOURS
        }
    except Exception:
        response.delete_cookie("refresh_token")
        raise InvalidTokenError





async def refresh_user_tokens(refresh_token: str, session: AsyncSession) -> Token:
    payload = await decode_refresh_token(refresh_token)
    user_id = payload.sub
    if not user_id:
        logger.error("BadCredentialsError")
        raise BadCredentialsError

    user = await get_user_by_id(access=FAKE_ACCESS_CONTEXT, user_id=user_id, session=session)

    if not user:
        logger.error("BadCredentialsError")
        raise BadCredentialsError
    if not user.is_active:
        logger.error("UserInactiveError")
        raise UserInactiveError

    role_names = await get_list_user_rolenames(
        access=FAKE_ACCESS_CONTEXT, session=session, user_id=user.id
    )
    new_access = create_access_token(
        data={"sub": str(user.id), "role": role_names}
    )
    new_refresh = create_refresh_token({"sub": str(user.id)})

    token_blacklist.ban(refresh_token)
    return Token(access_token=new_access, refresh_token=new_refresh)


async def refresh_access_token(refresh_token: str, session: AsyncSession) -> AccessToken:
    payload = await decode_refresh_token(refresh_token)
    user_id = payload.sub
    if not user_id:
        logger.error("BadCredentialsError")
        raise BadCredentialsError

    user = await get_user_by_id(access=FAKE_ACCESS_CONTEXT, user_id=user_id, session=session)

    if not user:
        logger.error("BadCredentialsError")
        raise BadCredentialsError
    if not user.is_active:
        logger.error("UserInactiveError")
        raise UserInactiveError

    role_names = await get_list_user_rolenames(
        access=FAKE_ACCESS_CONTEXT, session=session, user_id=user.id
    )
    new_access = create_access_token(
        data={"sub": str(user.id), "role": role_names}
    )
    access_token = new_access
    return access_token


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

        return await UserDAO.get_from_user_roles(session=session, user_id=filters.user_id)

    if "read_permission" in access.permissions:
        if filters.user_id is not None and filters.user_id != access.user_id:
            logger.error("PermissionDenied")
            raise PermissionDenied(
                custom_detail="Missing read or read_all permission on user_roles"
            )
        #filters.user_id = access.user_id
        return await get_list_user_rolenames(
            access=FAKE_ACCESS_CONTEXT, session=session, user_id=access.user_id
        )
        #return UserDAO.get_from_user_roles(session=session, user_id=filters.user_id)

    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing read or read_all permission on user_roles"
    )


async def ensure_user_is_active(user_id: UUID, session: AsyncSession) -> bool:
    user = await get_user_by_id(access=FAKE_ACCESS_CONTEXT, user_id=user_id, session=session)
    if user is None:
        raise BadCredentialsError
    if not user.is_active:
        raise UserInactiveError
    return True
