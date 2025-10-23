from typing import Any, Awaitable, Callable, List, Tuple, Optional
from uuid import UUID
import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain, Permission
from app.schemas.base import PaginationParams
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


logger = structlog.get_logger()


async def find_many_m2m(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    session: AsyncSession,
    filters: Optional[BaseModel] = None,
    pagination: Optional[PaginationParams] = None,
):
    if Permission.READ_ALL in access.permissions:
        logger.info(Permission.READ_ALL.value, filters=filters, pagination=pagination)
        result = await methodDAO.find_many(session=session, filters=filters)
        return result

    if Permission.READ in access.permissions:
        logger.info(Permission.READ.value, filters=filters, pagination=pagination)
        result = await methodDAO.find_many(session=session, filters=filters)
        return result

    custom_detail = f"Missing {Permission.READ.value} or {Permission.READ_ALL.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def find_one_m2m(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    session: AsyncSession,
    filters: Optional[BaseModel] = None,
):
    if Permission.READ_ALL in access.permissions:
        logger.info(Permission.READ_ALL.value, filters=filters)
        result = await methodDAO.find_one(session=session, filters=filters)
        return result

    if Permission.READ in access.permissions:
        logger.info(Permission.READ.value, filters=filters)
        result = await methodDAO.find_one(session=session, filters=filters)
        return result

    custom_detail = f"Missing {Permission.READ.value} or {Permission.READ_ALL.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)
