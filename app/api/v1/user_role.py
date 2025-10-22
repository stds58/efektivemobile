from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.private_router import private_route_dependency
from app.schemas.user_role import (
    SchemaUserRoleBase,
    SchemaUserRoleCreate,
    SchemaUserRoleFilter,
)
from app.services.user_role import (
    find_many_user_role,
    add_one_user_role,
    delete_one_user_role,
)
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()


router = APIRouter()

OWNER_FIELD = "user_id"


@router.get("", summary="Get user_roles")
async def get_orders(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaUserRoleFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    logger.info(
        "Get user_roles", owner_field=OWNER_FIELD, filters=filters, pagination=pagination
    )
    order = await find_many_user_role(
        business_element=BusinessDomain.USER_ROLES,
        access=request_context.access,
        filters=filters,
        session=request_context.session,
        pagination=pagination,
    )
    logger.info(
        "Geted user_roles", owner_field=OWNER_FIELD, filters=filters, pagination=pagination
    )
    return order


@router.post("", summary="Create user_role")
async def create_order(
    data: SchemaUserRoleCreate,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Add user_role", data=data)
    order = await add_one_user_role(
        business_element=BusinessDomain.USER_ROLES,
        access=request_context.access,
        data=data,
        session=request_context.session,
    )
    logger.info("Added user_role", data=data)
    return order


@router.delete(
    "/{user_role_id}", summary="Delete user_role", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    user_role_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Delete order", model_id=user_role_id)
    await delete_one_user_role(
        business_element=BusinessDomain.USER_ROLES,
        access=request_context.access,
        session=request_context.session,
        user_role_id=user_role_id,
    )
    logger.info("Deleted order", model_id=user_role_id)
    return
