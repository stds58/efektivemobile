from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_db import connection
from app.schemas.category import SchemaCategoryBase, SchemaCategoryCreate, SchemaCategoryFilter, SchemaCategoryPatch
from app.services.category import find_many_category , add_one_category , update_one_category , delete_one_category
from app.dependencies.permissions import require_permission
from app.schemas.permission import AccessContext



router = APIRouter()


@router.get("/category", summary="Get categorys")
async def get_categorys(
        filters: SchemaCategoryFilter = Depends(),
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("category")),
):
    return await find_many_category(access=access, filters=filters, session=session)


@router.post("", summary="Create category")
async def create_category(
        data: SchemaCategoryCreate,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("category"))
):
    category = await add_one_category(access=access, data=data, session=session)
    return category


@router.patch("/{id}", summary="Update category", response_model=SchemaCategoryBase)
async def edit_product(
        category_id: UUID,
        data: SchemaCategoryPatch,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("category"))
):
    updated_category = await update_one_category(access=access, data=data, session=session, category_id=category_id)
    return updated_category
