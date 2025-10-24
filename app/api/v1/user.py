from typing import List
from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.schemas.user import (
    SchemaUserPatch,
    SchemaUserFilter,
    SchemaUserBase,
    SchemaChangePasswordRequest,
)
from app.services.user import (
    find_many_user,
    update_user,
    soft_delete_user,
    user_change_password,
)  # , get_user_by_id
from app.dependencies.private_router import private_route_dependency
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext
from app.services.user_role import find_one_user_role_m2m
from app.schemas.user_role import (
    SchemaUserRoleFilter,
)


logger = structlog.get_logger()


router = APIRouter()


@router.get("/me", summary="Get user me", response_model=SchemaUserBase)
async def get_me(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    filters = SchemaUserRoleFilter(user_id=request_context.access.user_id)
    user = await find_one_user_role_m2m(
        business_element=BusinessDomain.USER_ROLES,
        access=request_context.access,
        filters=filters,
        session=request_context.session,
    )

    logger.info("Get user me")
    return user


@router.patch("/me", summary="Сhange_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    filters: SchemaChangePasswordRequest,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Сhange_password")
    await user_change_password(
        access=request_context.access,
        filters=filters,
        session=request_context.session,
        user_id=request_context.access.user_id,
    )
    logger.info("Сhanged_password")
    return


@router.get("", summary="Get users", response_model=List[SchemaUserBase])
async def get_users(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaUserFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    user = await find_many_user(
        business_element=BusinessDomain.USER,
        session=request_context.session,
        access=request_context.access,
        filters=filters,
        pagination=pagination,
    )
    logger.info("Get users", filters=filters, pagination=pagination)
    return user


@router.patch("/{user_id}", summary="Update user", response_model=SchemaUserBase)
async def edit_user(
    user_id: UUID,
    user_in: SchemaUserPatch,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    updated_user = await update_user(
        access=request_context.access,
        filters=user_in,
        session=request_context.session,
        user_id=user_id,
    )
    return updated_user


@router.delete(
    "/{user_id}", summary="Soft delete user", status_code=status.HTTP_204_NO_CONTENT
)
async def unactivate_user(
    user_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    """
    soft-delete не отзывает активные токены
    если админ будет отключать другого пользователя, то токены можно взять из белого списка токенов,
    а в данной системе есть только чёрный список.
    да и требования к системе не такие жёсткие - не страшно, если новость об отключении дойдёт до пользователя,
    когда он попытается взять новый токен.
    впрочем, в зависимости get_current_user есть проверка на user.is_active в бд.
    она заменяет белый список токенов
    """
    await soft_delete_user(
        access=request_context.access, session=request_context.session, user_id=user_id
    )
    return
