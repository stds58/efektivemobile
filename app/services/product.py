from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.product import ProductDAO
from app.schemas.base import PaginationParams
from app.schemas.product import (
    SchemaProductCreate,
    SchemaProductFilter,
    SchemaProductPatch,
)
from app.schemas.permission import AccessContext
from app.services.base import (
    find_many_business_element,
    add_one_business_element,
    update_one_business_element,
    delete_one_business_element,
)


logger = structlog.get_logger()


async def find_many_product(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaProductFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    return await find_many_business_element(
        business_element=business_element,
        methodDAO=ProductDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
    )


async def add_one_product(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaProductCreate,
    session: AsyncSession,
):
    return await add_one_business_element(
        business_element=business_element,
        methodDAO=ProductDAO,
        access=access,
        data=data,
        session=session,
    )


async def update_one_product(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaProductPatch,
    session: AsyncSession,
    product_id: UUID,
):
    return await update_one_business_element(
        business_element=business_element,
        methodDAO=ProductDAO,
        access=access,
        data=data,
        session=session,
        business_element_id=product_id,
    )


async def delete_one_product(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    product_id: UUID,
):
    return await delete_one_business_element(
        business_element=business_element,
        methodDAO=ProductDAO,
        access=access,
        session=session,
        business_element_id=product_id,
    )
