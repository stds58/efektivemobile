from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.product import ProductDAO
from app.schemas.base import PaginationParams
from app.schemas.product import (
    SchemaProductCreate,
    SchemaProductFilter,
    SchemaProductPatch,
)
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


async def find_many_product(
    access: AccessContext,
    filters: SchemaProductFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        return await ProductDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )
    if "read_permission" in access.permissions:
        return await ProductDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )
    raise PermissionDenied(
        custom_detail="Missing read or read_all permission on product"
    )


async def add_one_product(
    access: AccessContext, data: SchemaProductCreate, session: AsyncSession
):
    if "create_permission" in access.permissions:
        values_dict = data.model_dump(exclude_unset=True)
        return await ProductDAO.add_one(session=session, values=values_dict)
    raise PermissionDenied(custom_detail="Missing create permission on product")


async def update_one_product(
    access: AccessContext,
    data: SchemaProductPatch,
    session: AsyncSession,
    product_id: UUID,
):
    filters_dict = data.model_dump(exclude_unset=True)
    if "update_all_permission" in access.permissions:
        return await ProductDAO.update_one(
            model_id=product_id, session=session, values=filters_dict
        )
    if "update_permission" in access.permissions:
        return await ProductDAO.update_one(
            model_id=product_id, session=session, values=filters_dict
        )
    raise PermissionDenied(
        custom_detail="Missing update or update_all permission on product"
    )


async def delete_one_product(
    access: AccessContext, session: AsyncSession, product_id: UUID
):
    if "delete_all_permission" in access.permissions:
        return await ProductDAO.delete_one_by_id(model_id=product_id, session=session)
    if "delete_permission" in access.permissions:
        return await ProductDAO.delete_one_by_id(model_id=product_id, session=session)
    raise PermissionDenied(
        custom_detail="Missing delete or delete_all permission on product"
    )
