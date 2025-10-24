from typing import Optional, List
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.user_role import UserRoleDAO
from app.crud.user_m2m_role import UserRoleM2MDAO
from app.schemas.base import PaginationParams
from app.schemas.user import SchemaUserBase
from app.schemas.user_role import (
    SchemaUserRoleCreate,
    SchemaUserRoleFilter,
)
from app.schemas.permission import AccessContext
from app.services.base import (
    add_one_business_element,
    delete_one_business_element,
)
from app.services.base_m2m import find_one_m2m, find_many_m2m

logger = structlog.get_logger()


async def find_many_user_role_m2m(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    filters: Optional[SchemaUserRoleFilter] = None,
    pagination: Optional[PaginationParams] = None,
):
    user_roles = await find_many_m2m(
        business_element=business_element,
        methodDAO=UserRoleM2MDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
    )
    return user_roles


async def find_one_user_role_m2m(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaUserRoleFilter,
    session: AsyncSession,
):
    user_roles = await find_one_m2m(
        business_element=business_element,
        methodDAO=UserRoleM2MDAO,
        access=access,
        filters=filters,
        session=session,
    )
    return user_roles


async def find_one_user_role(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaUserRoleFilter,
    session: AsyncSession,
):
    user_roles = await find_one_m2m(
        business_element=business_element,
        methodDAO=UserRoleDAO,
        access=access,
        filters=filters,
        session=session,
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


async def get_list_user_rolenames(
    access: AccessContext,
    session: AsyncSession,
    user_id: UUID,
) -> List[str]:
    filters=SchemaUserRoleFilter(id=user_id)
    user_roles = await find_one_m2m(
        business_element="user_roles",
        methodDAO=UserRoleM2MDAO,
        access=access,
        filters=filters,
        session=session,
    )
    role_names = [role.name for role in user_roles.roles or []]
    return role_names


async def get_user_with_roles(
    access: AccessContext,
    session: AsyncSession,
    user_id: UUID,
) -> SchemaUserBase:
    filters=SchemaUserRoleFilter(id=user_id)
    user_with_roles = await find_one_m2m(
        business_element="user_roles",
        methodDAO=UserRoleM2MDAO,
        access=access,
        filters=filters,
        session=session,
    )
    return user_with_roles
