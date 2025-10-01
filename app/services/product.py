from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.product import ProductDAO
from app.schemas.product import SchemaProductBase, SchemaProductCreate, SchemaProductFilter
from app.services.user import UserService
from app.schemas.permission import AccessContext
from app.exceptions.base import PermissionDenied


async def find_many_product(access: AccessContext, filters: SchemaProductFilter, session: AsyncSession):
    if "read_all_permission" in access.permissions:
        products = await ProductDAO.find_many(filters=filters, session=session)
    elif "read_permission" in access.permissions:
        filters.user_id = access.user_id
        products = await ProductDAO.find_many(filters=filters, session=session)
    else:
        raise PermissionDenied(custom_detail="Missing read or read_all permission on product")
    return products

