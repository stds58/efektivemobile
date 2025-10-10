import structlog
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.order import OrderDAO
from app.schemas.base import PaginationParams
from app.schemas.order import SchemaOrderCreate, SchemaOrderFilter, SchemaOrderPatch
from app.schemas.permission import AccessContext
from app.services.base_scoped_operations import find_many_scoped
from app.exceptions.base import PermissionDenied


logger = structlog.get_logger()


async def find_many_order(
        business_element: BusinessDomain,
        access: AccessContext,
        filters: SchemaOrderFilter,
        session: AsyncSession,
        pagination: PaginationParams,
):
    return await find_many_scoped(
        business_element=business_element,
        methodDAO=OrderDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
        owner_field="user_id"
    )


async def add_one_order(
    access: AccessContext, data: SchemaOrderCreate, session: AsyncSession
):
    if "create_permission" in access.permissions:
        values_dict = data.model_dump(exclude_unset=True)
        values_dict["user_id"] = access.user_id
        return await OrderDAO.add_one(session=session, values=values_dict)

    logger.error("PermissionDenied")
    raise PermissionDenied(custom_detail="Missing create permission on order")


async def update_one_order(
    access: AccessContext, data: SchemaOrderPatch, session: AsyncSession, order_id: UUID
):
    filters_dict = data.model_dump(exclude_unset=True)

    if "update_all_permission" in access.permissions:
        return await OrderDAO.update_one(
            model_id=order_id, session=session, values=filters_dict
        )

    if "update_permission" in access.permissions:
        filter_obj = SchemaOrderFilter(order_id=order_id)
        order = await OrderDAO.find_one(filters=filter_obj, session=session)

        if access.user_id == order.user_id:
            return await OrderDAO.update_one(
                model_id=order_id, session=session, values=filters_dict
            )
        logger.error("PermissionDenied")
        raise PermissionDenied(
            custom_detail="Missing update or update_all permission on order"
        )

    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing update or update_all permission on order"
    )


async def delete_one_order(
    access: AccessContext, session: AsyncSession, order_id: UUID
):
    if "delete_all_permission" in access.permissions:
        return await OrderDAO.delete_one_by_id(model_id=order_id, session=session)

    if "delete_permission" in access.permissions:
        filter_obj = SchemaOrderFilter(order_id=order_id)
        order = await OrderDAO.find_one(filters=filter_obj, session=session)

        if access.user_id == order.user_id:
            return await OrderDAO.delete_one_by_id(model_id=order_id, session=session)
        logger.error("PermissionDenied")
        raise PermissionDenied(
            custom_detail="Missing delete or delete_all permission on order"
        )

    logger.error("PermissionDenied")
    raise PermissionDenied(
        custom_detail="Missing delete or delete_all permission on order"
    )
