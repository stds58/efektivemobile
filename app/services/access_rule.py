from uuid import UUID
from typing import Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain, Permission
from app.crud.access_rule import AccessRuleDAO
from app.crud.business_element import BusinessElementDAO
from app.schemas.base import PaginationParams
from app.schemas.access_rule import SchemaAccessRuleFilter, SchemaAccessRulePatch
from app.schemas.business_element import SchemaBusinessElementFilter
from app.schemas.permission import AccessContext
from app.services.base import (
    find_one_business_element,
    find_many_business_element,
    update_one_business_element,
)


logger = structlog.get_logger()


async def find_many_access_rule(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    filters: Optional[SchemaAccessRuleFilter] = None,
    pagination: Optional[PaginationParams] = None,

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


async def get_user_access_rules_for_business_element(
    access: AccessContext,
    session: AsyncSession,
    role_id: UUID,
    search_businesselement: BusinessDomain,
):
    filters = SchemaBusinessElementFilter(name=search_businesselement.value)
    b_elemets = await find_one_business_element(
        business_element=BusinessDomain.ACCESS_RULES,
        methodDAO=BusinessElementDAO,
        access=access,
        filters=filters,
        session=session,
    )
    businesselement_id = b_elemets.id

    filters = SchemaAccessRuleFilter(role_id=role_id, businesselement_id=businesselement_id)
    access_rule = await find_one_business_element(
        business_element=BusinessDomain.ACCESS_RULES,
        methodDAO=AccessRuleDAO,
        access=access,
        filters=filters,
        session=session,
    )

    if not access_rule:
        return []

    active_permissions = [
        perm.value
        for perm in Permission
        if getattr(access_rule, perm.value, False)
    ]

    return active_permissions
