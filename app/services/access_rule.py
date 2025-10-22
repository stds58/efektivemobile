from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.access_rule import AccessRuleDAO
from app.schemas.base import PaginationParams
from app.schemas.access_rule import SchemaAccessRuleFilter, SchemaAccessRulePatch
from app.schemas.permission import AccessContext
from app.services.base import (
    find_many_business_element,
    update_one_business_element,
)


logger = structlog.get_logger()


async def find_many_access_rule(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaAccessRuleFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    return await find_many_business_element(
        business_element=business_element,
        methodDAO=AccessRuleDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
    )


async def update_one_access_rule(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaAccessRulePatch,
    session: AsyncSession,
    access_rule_id: UUID,
):
    return await update_one_business_element(
        business_element=business_element,
        methodDAO=AccessRuleDAO,
        access=access,
        data=data,
        session=session,
        business_element_id=access_rule_id,
    )
