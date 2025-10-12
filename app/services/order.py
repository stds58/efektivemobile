from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.order import OrderDAO
from app.schemas.base import PaginationParams
from app.schemas.order import SchemaOrderCreate, SchemaOrderFilter, SchemaOrderPatch
from app.schemas.permission import AccessContext
from app.services.base_scoped_operations import (
    find_many_scoped,
    add_one_scoped,
    update_one_scoped,
    delete_one_scoped,
)


logger = structlog.get_logger()


async def find_many_order(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaOrderFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    return await find_many_scoped(
        business_element=business_element,
        methodDAO=OrderDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
        owner_field="user_id",
    )


async def add_one_order(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaOrderCreate,
    session: AsyncSession,
):
    return await add_one_scoped(
        business_element=business_element,
        methodDAO=OrderDAO,
        access=access,
        data=data,
        session=session,
    )


async def update_one_order(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaOrderPatch,
    session: AsyncSession,
    order_id: UUID,
):
    return await update_one_scoped(
        business_element=business_element,
        methodDAO=OrderDAO,
        access=access,
        data=data,
        session=session,
        business_element_id=order_id,
    )


async def delete_one_order(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    order_id: UUID,
):
    return await delete_one_scoped(
        business_element=business_element,
        methodDAO=OrderDAO,
        access=access,
        session=session,
        business_element_id=order_id,
    )
