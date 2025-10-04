from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_db import connection
from app.schemas.access_rule import (
    SchemaAccessRuleBase,
    SchemaAccessRuleFilter,
    SchemaAccessRulePatch,
)
from app.services.access_rule import find_many_access_rule, update_one_access_rule
from app.dependencies.permissions import require_permission
from app.schemas.permission import AccessContext
from app.schemas.base import PaginationParams


router = APIRouter()


@router.get("", summary="Get access_rules")
async def get_access_rules(
    filters: SchemaAccessRuleFilter = Depends(),
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("access_rule")),
    pagination: PaginationParams = Depends(),
):
    return await find_many_access_rule(
        access=access, filters=filters, session=session, pagination=pagination
    )


@router.patch(
    "/{id}", summary="Update access_rule", response_model=SchemaAccessRuleBase
)
async def edit_product(
    access_rule_id: UUID,
    data: SchemaAccessRulePatch,
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("access_rule")),
):
    return await update_one_access_rule(
        access=access, data=data, session=session, access_rule_id=access_rule_id
    )
