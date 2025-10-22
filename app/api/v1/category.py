from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.private_router import private_route_dependency
from app.schemas.category import (
    SchemaCategoryBase,
    SchemaCategoryCreate,
    SchemaCategoryFilter,
    SchemaCategoryPatch,
)
from app.services.category import (
    find_many_category,
    add_one_category,
    update_one_category,
    delete_one_category,
)
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()

router = APIRouter()


@router.get("", summary="Get categorys")
async def get_categorys(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.CATEGORY,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaCategoryFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    logger.info("Get categorys", filters=filters, pagination=pagination)
    category = await find_many_category(
        business_element=BusinessDomain.CATEGORY,
        session=request_context.session,
        access=request_context.access,
        filters=filters,
        pagination=pagination,
    )
    logger.info("Geted categorys", filters=filters, pagination=pagination)
    return category


@router.post("", summary="Create category")
async def create_category(
    data: SchemaCategoryCreate,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.CATEGORY,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Add category", data=data)
    category = await add_one_category(
        business_element=BusinessDomain.CATEGORY,
        access=request_context.access,
        data=data,
        session=request_context.session,
    )
    logger.info("Added category", data=data)
    return category


@router.patch(
    "/{category_id}", summary="Update category", response_model=SchemaCategoryBase
)
async def edit_product(
    category_id: UUID,
    data: SchemaCategoryPatch,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.CATEGORY,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Update category", data=data, model_id=category_id)
    updated_category = await update_one_category(
        business_element=BusinessDomain.CATEGORY,
        access=request_context.access,
        data=data,
        session=request_context.session,
        category_id=category_id,
    )
    logger.info("Updated category", data=data, model_id=category_id)
    return updated_category


@router.delete(
    "/{category_id}", summary="Delete category", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.CATEGORY,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Delete category", model_id=category_id)
    await delete_one_category(
        business_element=BusinessDomain.CATEGORY,
        access=request_context.access,
        session=request_context.session,
        category_id=category_id,
    )
    logger.info("Deleted category", model_id=category_id)
    return
