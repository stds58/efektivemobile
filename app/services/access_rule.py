import structlog
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.access_rule import AccessRuleDAO
from app.schemas.base import PaginationParams
from app.schemas.access_rule import SchemaAccessRuleFilter, SchemaAccessRulePatch
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


logger = structlog.get_logger()


async def find_many_access_rule(
    access: AccessContext,
    filters: SchemaAccessRuleFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        return await AccessRuleDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )
    if "read_permission" in access.permissions:
        return await AccessRuleDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )
    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing read or read_all permission on access_rule"
    )


async def update_one_access_rule(
    access: AccessContext,
    data: SchemaAccessRulePatch,
    session: AsyncSession,
    access_rule_id: UUID,
):
    filters_dict = data.model_dump(exclude_unset=True)
    if "update_all_permission" in access.permissions:
        return await AccessRuleDAO.update_one(
            model_id=access_rule_id, session=session, values=filters_dict
        )
    if "update_permission" in access.permissions:
        return await AccessRuleDAO.update_one(
            model_id=access_rule_id, session=session, values=filters_dict
        )
    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing update or update_all permission on access_rule"
    )
