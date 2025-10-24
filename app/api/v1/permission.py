from typing import List
import structlog
from fastapi import APIRouter, Depends
from app.core.enums import BusinessDomain, IsolationLevel
from app.services.user import (
    add_role_to_user,
    remove_role_from_user,
    get_all_user_roles,
)
from app.dependencies.private_router import private_route_dependency
from app.schemas.permission import (
    SchemaUserRolesBase,
    SchemaUserRolesCreate,
    SchemaUserRolesFilter,
)
from app.schemas.permission import RequestContext


logger = structlog.get_logger()

router = APIRouter()


OWNER_FIELD = "user_id"


@router.get("", summary="Get roles") # response_model=List[dict],
async def get_users(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaUserRolesFilter = Depends(),
):
    return await get_all_user_roles(
        filters=filters, access=request_context.access, session=request_context.session
    )


@router.post("", summary="Add role", response_model=SchemaUserRolesBase)
async def edit_user(
   request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    data: SchemaUserRolesCreate = Depends(),
):
    updated_user = await add_role_to_user(
        access=request_context.access, session=request_context.session, data=data
    )
    return updated_user


@router.delete("", summary="Delete role", response_model=dict)
async def unactivate_user(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    data: SchemaUserRolesCreate = Depends(),
):
    removed_user = await remove_role_from_user(
        access=request_context.access, session=request_context.session, data=data
    )
    return removed_user
