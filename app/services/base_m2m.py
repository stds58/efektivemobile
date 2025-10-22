from typing import Any, Awaitable, Callable, List, Tuple
from uuid import UUID
import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.schemas.base import PaginationParams
from app.schemas.permission import AccessContext
from app.schemas.user import SchemaUserBase, SchemaUserFilter
from app.exceptions.base import PermissionDenied
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
#from collections import defaultdict
from app.schemas.user import SchemaUserBase
from app.crud.user_m2m_role import UserRoleM2MDAO


logger = structlog.get_logger()


async def find_many_m2m(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    filters: BaseModel,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        logger.info("read_all_permission", filters=filters, pagination=pagination)
        result = await methodDAO.find_many(session=session, filters=filters)
        return result

    if "read_permission" in access.permissions:
        logger.info("read_permission", filters=filters, pagination=pagination)
        result = await methodDAO.find_many(session=session, filters=filters)
        return result

    custom_detail = f"Missing read or read_all permission on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def find_one_m2m(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    filters: BaseModel,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        logger.info("read_all_permission", filters=filters, pagination=pagination)
        result = await methodDAO.find_one(session=session, filters=filters)
        return result

    if "read_permission" in access.permissions:
        logger.info("read_permission", filters=filters, pagination=pagination)
        result = await methodDAO.find_one(session=session, filters=filters)
        return result

    custom_detail = f"Missing read or read_all permission on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)
