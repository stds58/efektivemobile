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
from app.crud.user_m2m_role import UserRolesDAO


logger = structlog.get_logger()


async def find_many_business_element_m2m(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    filters: BaseModel,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        logger.info("read_all_permission", filters=filters, pagination=pagination)
        result = await UserRolesDAO.find_many(
            session=session,
        )
        #print("result ",result)
        filters = SchemaUserFilter(id = "69e0bc18-1d59-4ea2-bf6c-f6684acde294",
    created_at = None,
    updated_at = None,
    email = None,
    first_name = None,
    last_name = None,
    is_active = None)
        one = await UserRolesDAO.find_one(
            session=session,
            filters=filters,
        )
        print("one ====!!!!!!!!!!!!! ", one)
        return result

    if "read_permission" in access.permissions:
        logger.info("read_permission", filters=filters, pagination=pagination)
        result = await UserRolesDAO.find_many(
            session=session,
        )
        return result

    custom_detail = f"Missing read or read_all permission on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def find_many_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    filters: BaseModel,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        logger.info("read_all_permission", filters=filters, pagination=pagination)
        return await methodDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )

    if "read_permission" in access.permissions:
        logger.info("read_permission", filters=filters, pagination=pagination)
        return await methodDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )

    custom_detail = f"Missing read or read_all permission on {business_element.value}"
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def add_one_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    data: BaseModel,
    session: AsyncSession,
):
    if "create_permission" in access.permissions:
        values_dict = data.model_dump(exclude_unset=True)
        result = await methodDAO.add_one(session=session, values=values_dict)
        await session.commit()
        return result

    custom_detail = f"Missing create permission on {business_element.value}"
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
    if "update_all_permission" in access.permissions:
        result = await methodDAO.update_one(model_id=business_element_id, session=session, values=filters_dict)
        await session.commit()
        return result
    if "update_permission" in access.permissions:
        result = await methodDAO.update_one(model_id=business_element_id, session=session, values=filters_dict)
        await session.commit()
        return result

    custom_detail = (
        f"Missing update or update_all permission on {business_element.value}"
    )
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)


async def delete_one_business_element(
    business_element: BusinessDomain,
    methodDAO: Callable[..., Awaitable[Any]],
    access: AccessContext,
    session: AsyncSession,
    business_element_id: UUID,
):
    if "delete_all_permission" in access.permissions:
        result = await methodDAO.delete_one_by_id(model_id=business_element_id, session=session)
        await session.commit()
        return result
    if "delete_permission" in access.permissions:
        result = await methodDAO.delete_one_by_id(model_id=business_element_id, session=session)
        await session.commit()
        return result

    custom_detail = (
        f"Missing delete or delete_all permission on {business_element.value}"
    )
    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)
