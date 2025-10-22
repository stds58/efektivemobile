from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.user_role import UserRoleDAO
from app.crud.role import RoleDAO
from app.schemas.base import PaginationParams
from app.schemas.user_role import (
    SchemaUserRoleCreate,
    SchemaUserRoleFilter,
)
from app.schemas.permission import AccessContext
from app.services.base import (
    find_many_business_element,
    add_one_business_element,
    delete_one_business_element,
    find_many_business_element_m2m,
)


logger = structlog.get_logger()


async def find_many_user_role(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaUserRoleFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    user_roles = await find_many_business_element_m2m(
        business_element=business_element,
        methodDAO=UserRoleDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
    )
    return user_roles


async def add_one_user_role(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaUserRoleCreate,
    session: AsyncSession,
):
    return await add_one_business_element(
        business_element=business_element,
        methodDAO=UserRoleDAO,
        access=access,
        data=data,
        session=session,
    )


async def delete_one_user_role(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    user_role_id: UUID,
):
    return await delete_one_business_element(
        business_element=business_element,
        methodDAO=UserRoleDAO,
        access=access,
        session=session,
        business_element_id=user_role_id,
    )
