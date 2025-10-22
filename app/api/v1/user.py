from typing import List
from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.schemas.user import SchemaUserPatch, SchemaUserFilter, SchemaUserBase
from app.services.user import find_many_user, update_user, soft_delete_user
from app.dependencies.private_router import private_route_dependency
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()


router = APIRouter()


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


@router.patch("/{id}", summary="Update user", response_model=SchemaUserBase)
async def edit_user(
    user_id: UUID,
    user_in: SchemaUserPatch,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    updated_user = await update_user(
        access=request_context.access, filters=user_in, session=request_context.session, user_id=user_id
    )
    return updated_user


@router.delete(
    "/{id}", summary="Soft delete user", status_code=status.HTTP_204_NO_CONTENT
)
async def unactivate_user(
    user_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    await soft_delete_user(access=request_context.access, session=request_context.session, user_id=user_id)
    return
