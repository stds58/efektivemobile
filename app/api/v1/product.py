from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.get_db import auth_db_context
from app.schemas.product import (
    SchemaProductBase,
    SchemaProductCreate,
    SchemaProductFilter,
    SchemaProductPatch,
)
from app.services.product import (
    find_many_product,
    add_one_product,
    update_one_product,
    delete_one_product,
)
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()


router = APIRouter()


@router.get("", summary="Get products")
async def get_products(
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.PRODUCT,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=False,
        )
    ),
    filters: SchemaProductFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    logger.info("Get products", filters=filters, pagination=pagination)
    product = await find_many_product(
        business_element=BusinessDomain.PRODUCT,
        session=request_context.session,
        access=request_context.access,
        filters=filters,
        pagination=pagination,
    )
    logger.info("Geted products", filters=filters, pagination=pagination)
    return product


@router.post("", summary="Create product")
async def create_product(
    data: SchemaProductCreate,
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.PRODUCT,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=True,
        )
    ),
):
    logger.info("Add product", data=data)
    product = await add_one_product(
        business_element=BusinessDomain.PRODUCT,
        access=request_context.access,
        data=data,
        session=request_context.session,
    )
    logger.info("Added product", data=data)
    return product


@router.patch(
    "/{product_id}", summary="Update product", response_model=SchemaProductBase
)
async def edit_product(
    product_id: UUID,
    data: SchemaProductPatch,
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.PRODUCT,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=True,
        )
    ),
):
    logger.info("Update product", data=data, model_id=product_id)
    updated_product = await update_one_product(
        business_element=BusinessDomain.PRODUCT,
        access=request_context.access,
        data=data,
        session=request_context.session,
        product_id=product_id,
    )
    logger.info("Updated product", data=data, model_id=product_id)
    return updated_product


@router.delete(
    "/{product_id}", summary="Delete product", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    product_id: UUID,
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.PRODUCT,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=True,
        )
    ),
):
    logger.info("Delete product", model_id=product_id)
    await delete_one_product(
        business_element=BusinessDomain.PRODUCT,
        access=request_context.access,
        session=request_context.session,
        product_id=product_id,
    )
    logger.info("Deleted product", model_id=product_id)
    return
