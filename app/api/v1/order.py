from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.private_router import private_route_dependency
from app.schemas.order import (
    SchemaOrderBase,
    SchemaOrderCreate,
    SchemaOrderFilter,
    SchemaOrderPatch,
)
from app.services.order import (
    find_many_order,
    add_one_order,
    update_one_order,
    delete_one_order,
)
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()


router = APIRouter()

OWNER_FIELD = "user_id"


@router.get("", summary="Get orders")
async def get_orders(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.ORDER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaOrderFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    logger.info(
        "Get orders", owner_field=OWNER_FIELD, filters=filters, pagination=pagination
    )
    order = await find_many_order(
        business_element=BusinessDomain.ORDER,
        access=request_context.access,
        filters=filters,
        session=request_context.session,
        pagination=pagination,
    )
    logger.info(
        "Geted orders", owner_field=OWNER_FIELD, filters=filters, pagination=pagination
    )
    return order


@router.post("", summary="Create order")
async def create_order(
    data: SchemaOrderCreate,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.ORDER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Add order", data=data)
    order = await add_one_order(
        business_element=BusinessDomain.ORDER,
        access=request_context.access,
        data=data,
        session=request_context.session,
    )
    logger.info("Added order", data=data)
    return order


@router.patch("/{order_id}", summary="Update order", response_model=SchemaOrderBase)
async def edit_order(
    order_id: UUID,
    data: SchemaOrderPatch,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.ORDER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Update order", data=data, model_id=order_id)
    updated_order = await update_one_order(
        business_element=BusinessDomain.ORDER,
        access=request_context.access,
        data=data,
        session=request_context.session,
        order_id=order_id,
    )
    logger.info("Updated order", data=data, model_id=order_id)
    return updated_order


@router.delete(
    "/{order_id}", summary="Delete order", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    order_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.ORDER,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Delete order", model_id=order_id)
    await delete_one_order(
        business_element=BusinessDomain.ORDER,
        access=request_context.access,
        session=request_context.session,
        order_id=order_id,
    )
    logger.info("Deleted order", model_id=order_id)
    return
