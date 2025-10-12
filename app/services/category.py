from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.category import CategoryDAO
from app.schemas.base import PaginationParams
from app.schemas.category import (
    SchemaCategoryCreate,
    SchemaCategoryFilter,
    SchemaCategoryPatch,
)
from app.schemas.permission import AccessContext
from app.services.base import (
    find_many_business_element,
    add_one_business_element,
    update_one_business_element,
    delete_one_business_element,
)


logger = structlog.get_logger()


async def find_many_category(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaCategoryFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    return await find_many_business_element(
        business_element=business_element,
        methodDAO=CategoryDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
    )


async def add_one_category(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaCategoryCreate,
    session: AsyncSession,
):
    return await add_one_business_element(
        business_element=business_element,
        methodDAO=CategoryDAO,
        access=access,
        data=data,
        session=session,
    )


async def update_one_category(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaCategoryPatch,
    session: AsyncSession,
    category_id: UUID,
):
    return await update_one_business_element(
        business_element=business_element,
        methodDAO=CategoryDAO,
        access=access,
        data=data,
        session=session,
        business_element_id=category_id,
    )


async def delete_one_category(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    category_id: UUID,
):
    return await delete_one_business_element(
        business_element=business_element,
        methodDAO=CategoryDAO,
        access=access,
        session=session,
        business_element_id=category_id,
    )
