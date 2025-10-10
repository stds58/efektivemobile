import structlog
from typing import Any, Awaitable, Callable
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.schemas.base import PaginationParams
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


logger = structlog.get_logger()


async def find_many_scoped(
        business_element: BusinessDomain,
        methodDAO: Callable[..., Awaitable[Any]],
        access: AccessContext,
        filters: BaseModel,
        session: AsyncSession,
        pagination: PaginationParams,
        owner_field: str
):
    custom_detail = f"Missing read or read_all permission on {business_element.value}"

    if "read_all_permission" in access.permissions:
        logger.info("read_all_permission", filters=filters, pagination=pagination)
        return await methodDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )

    if "read_permission" in access.permissions:
        logger.info("read_permission", filters=filters, pagination=pagination)
        # Получаем текущее значение поля владельца из фильтров
        current_owner_value = getattr(filters, owner_field, None)

        # Если в фильтре указан владелец, и он не совпадает с текущим пользователем - ошибка
        if current_owner_value is not None and current_owner_value != access.user_id:
            logger.error("PermissionDenied on read_permission", error=custom_detail)
            raise PermissionDenied(custom_detail=custom_detail)

        # Устанавливаем фильтр на текущего пользователя
        setattr(filters, owner_field, access.user_id)

        return await methodDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )

    logger.error("PermissionDenied", error=custom_detail)
    raise PermissionDenied(custom_detail=custom_detail)









