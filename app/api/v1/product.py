from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.dependencies.get_db import connection
from app.schemas.product import SchemaProductBase, SchemaProductCreate, SchemaProductFilter
from app.services.product import find_many_product
from app.dependencies.permissions import require_permission
from app.schemas.permission import AccessContext



router = APIRouter()


@router.get("/product", summary="Get products")
async def get_products(
        filters: SchemaProductFilter = Depends(),
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("product")),
):
    return await find_many_product(access=access, filters=filters, session=session)


# @router.post("", summary="Create order")
# async def create_product(data: SchemaProductCreate, session: AsyncSession = Depends(connection())):
#     order = await add_one_product(data=data, session=session)
#     return {"data": order}
