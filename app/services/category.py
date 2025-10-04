from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.category import CategoryDAO
from app.schemas.base import PaginationParams
from app.schemas.category import (
    SchemaCategoryCreate,
    SchemaCategoryFilter,
    SchemaCategoryPatch,
)
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


async def find_many_category(
    access: AccessContext,
    filters: SchemaCategoryFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    if "read_all_permission" in access.permissions:
        return await CategoryDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )
    if "read_permission" in access.permissions:
        return await CategoryDAO.find_many(
            filters=filters, session=session, pagination=pagination
        )
    raise PermissionDenied(
        custom_detail="Missing read or read_all permission on category"
    )


async def add_one_category(
    access: AccessContext, data: SchemaCategoryCreate, session: AsyncSession
):
    if "create_permission" in access.permissions:
        values_dict = data.model_dump(exclude_unset=True)
        return await CategoryDAO.add_one(session=session, values=values_dict)
    raise PermissionDenied(custom_detail="Missing create permission on category")


async def update_one_category(
    access: AccessContext,
    data: SchemaCategoryPatch,
    session: AsyncSession,
    category_id: UUID,
):
    filters_dict = data.model_dump(exclude_unset=True)
    if "update_all_permission" in access.permissions:
        return await CategoryDAO.update_one(
            model_id=category_id, session=session, values=filters_dict
        )
    if "update_permission" in access.permissions:
        return await CategoryDAO.update_one(
            model_id=category_id, session=session, values=filters_dict
        )
    raise PermissionDenied(
        custom_detail="Missing update or update_all permission on category"
    )


async def delete_one_category(
    access: AccessContext, session: AsyncSession, category_id: UUID
):
    if "delete_all_permission" in access.permissions:
        return await CategoryDAO.delete_one_by_id(model_id=category_id, session=session)
    if "delete_permission" in access.permissions:
        return await CategoryDAO.delete_one_by_id(model_id=category_id, session=session)
    raise PermissionDenied(
        custom_detail="Missing delete or delete_all permission on category"
    )
