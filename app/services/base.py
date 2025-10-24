from typing import Any, Awaitable, Callable
from uuid import UUID
import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain, Permission
from app.schemas.base import PaginationParams
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


logger = structlog.get_logger()


async def find_many_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    filters: BaseModel,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if Permission.READ_ALL in access.permissions:
        logger.info(Permission.READ_ALL.value, filters=filters, pagination=pagination)
        return await methodDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )

    if Permission.READ in access.permissions:
        logger.info(Permission.READ.value, filters=filters, pagination=pagination)
        return await methodDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )

    custom_detail = f"Missing {Permission.READ.value} or {Permission.READ_ALL.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def find_one_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    filters: BaseModel,
    session: AsyncSession,
):
    if Permission.READ_ALL in access.permissions:
        logger.info(Permission.READ_ALL.value, filters=filters)
        return await methodDAO.find_one(
            filters=filters,
            session=session,
        )

    if Permission.READ in access.permissions:
        logger.info(Permission.READ.value, filters=filters)
        return await methodDAO.find_one(filters=filters, session=session)

    custom_detail = f"Missing {Permission.READ.value} or {Permission.READ_ALL.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def add_one_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    data: BaseModel,
    session: AsyncSession,
):
    if Permission.CREATE in access.permissions:
        values_dict = data.model_dump(exclude_unset=True)
        logger.info(Permission.CREATE.value, filters=values_dict)
        result = await methodDAO.add_one(session=session, values=values_dict)
        await session.commit()
        return result

    custom_detail = f"Missing {Permission.CREATE.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def update_one_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    data: BaseModel,
    session: AsyncSession,
    business_element_id: UUID,
):
    filters_dict = data.model_dump(exclude_unset=True)
    if Permission.UPDATE_ALL in access.permissions:
        logger.info(
            Permission.UPDATE_ALL.value,
            model_id=business_element_id,
            filters=filters_dict,
        )
        result = await methodDAO.update_one(
            model_id=business_element_id, session=session, values=filters_dict
        )
        await session.commit()
        return result
    if Permission.UPDATE in access.permissions:
        logger.info(
            Permission.UPDATE.value, model_id=business_element_id, filters=filters_dict
        )
        result = await methodDAO.update_one(
            model_id=business_element_id, session=session, values=filters_dict
        )
        await session.commit()
        return result

    custom_detail = f"Missing {Permission.UPDATE.value} or {Permission.UPDATE_ALL.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def delete_one_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    session: AsyncSession,
    business_element_id: UUID,
):
    if Permission.DELETE_ALL in access.permissions:
        logger.info(Permission.DELETE_ALL.value, model_id=business_element_id)
        result = await methodDAO.delete_one_by_id(
            model_id=business_element_id, session=session
        )
        await session.commit()
        return result
    if Permission.DELETE in access.permissions:
        logger.info(Permission.DELETE.value, model_id=business_element_id)
        result = await methodDAO.delete_one_by_id(
            model_id=business_element_id, session=session
        )
        await session.commit()
        return result

    custom_detail = f"Missing {Permission.DELETE.value} or {Permission.DELETE_ALL.value} on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)
