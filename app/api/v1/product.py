from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_db import connection
from app.schemas.product import SchemaProductBase, SchemaProductCreate, SchemaProductFilter, SchemaProductPatch
from app.services.product import find_many_product, add_one_product, update_one_product, delete_one_product
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


@router.post("", summary="Create product")
async def create_product(
        data: SchemaProductCreate,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("product"))
):
    product = await add_one_product(access=access, data=data, session=session)
    return product


@router.patch("/{id}", summary="Update product", response_model=SchemaProductBase)
async def edit_product(
        product_id: UUID,
        data: SchemaProductPatch,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("product"))
):
    updated_product = await update_one_product(access=access, data=data, session=session, product_id=product_id)
    return updated_product
