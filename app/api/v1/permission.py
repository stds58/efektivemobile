from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.services.user import (
    add_role_to_user,
    get_all_user_roles,
)
from app.services.user_role import delete_one_user_role, find_one_user_role
from app.dependencies.private_router import private_route_dependency
from app.schemas.permission import (
    SchemaUserRolesCreate,
    SchemaUserRolesFilter,
)
from app.schemas.user_role import SchemaUserRoleFilter
from app.schemas.permission import RequestContext
from app.schemas.user import SchemaUserBase
from app.exceptions.base import ObjectsNotFoundByIDError


logger = structlog.get_logger()

router = APIRouter()


OWNER_FIELD = "user_id"


@router.get("", summary="Get roles", response_model=SchemaUserBase)
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


@router.post("", summary="Add role", response_model=SchemaUserBase)
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
    filters = SchemaUserRolesFilter(
        user_id=updated_user.user_id, role_id=updated_user.role_id
    )
    return await get_all_user_roles(
        filters=filters, access=request_context.access, session=request_context.session
    )


@router.delete(
    "/{user_id}/{role_id}",
    summary="Remove role from user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_role(
    user_id: UUID,
    role_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.USER_ROLES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    filters = SchemaUserRoleFilter(user_id=user_id, role_id=role_id)
    user_role = await find_one_user_role(
        business_element=BusinessDomain.USER_ROLES,
        access=request_context.access,
        filters=filters,
        session=request_context.session,
    )
    if user_role is None:
        raise ObjectsNotFoundByIDError
    await delete_one_user_role(
        business_element=BusinessDomain.USER_ROLES,
        access=request_context.access,
        session=request_context.session,
        user_role_id=user_role.id,
    )
    return
