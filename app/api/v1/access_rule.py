from uuid import UUID
import structlog
from fastapi import APIRouter, Depends
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.private_router import private_route_dependency
from app.schemas.access_rule import (
    SchemaAccessRuleBase,
    SchemaAccessRuleFilter,
    SchemaAccessRulePatch,
)
from app.services.access_rule import find_many_access_rule, update_one_access_rule
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()

router = APIRouter()


@router.get("", summary="Get access rules")
async def get_access_rules(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.ACCESS_RULES,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaAccessRuleFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    logger.info("Get access rules", filters=filters, pagination=pagination)
    access_rule = await find_many_access_rule(
        business_element=BusinessDomain.ACCESS_RULES,
        session=request_context.session,
        access=request_context.access,
        filters=filters,
        pagination=pagination,
    )
    logger.info("Geted access rules", filters=filters, pagination=pagination)
    return access_rule


@router.patch("/{access_rule_id}", summary="Update access_rule", response_model=SchemaAccessRuleBase)
async def edit_access_rule(
    access_rule_id: UUID,
    data: SchemaAccessRulePatch,
        request_context: RequestContext = private_route_dependency(
            business_element=BusinessDomain.ACCESS_RULES,
            isolation_level=IsolationLevel.REPEATABLE_READ,
        ),
):
    logger.info("Update access_rule", data=data, model_id=access_rule_id)
    updated_product = await update_one_access_rule(
        business_element=BusinessDomain.ACCESS_RULES,
        access=request_context.access,
        data=data,
        session=request_context.session,
        access_rule_id=access_rule_id,
    )
    logger.info("Updated access_rule", data=data, model_id=access_rule_id)
    return updated_product
