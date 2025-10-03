from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_db import connection
from app.schemas.order import SchemaOrderBase, SchemaOrderCreate, SchemaOrderFilter, SchemaOrderPatch
from app.services.order import find_many_order, add_one_order, update_one_order, delete_one_order
from app.dependencies.permissions import require_permission
from app.schemas.permission import AccessContext


router = APIRouter()


@router.get("", summary="Get orders")
async def get_orders(
        filters: SchemaOrderFilter = Depends(),
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("order")),
):
    return await find_many_order(access=access, filters=filters, session=session)


@router.post("", summary="Create order")
async def create_order(
        data: SchemaOrderCreate,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("order"))
):
    return await add_one_order(access=access, data=data, session=session)


@router.patch("/{id}", summary="Update order", response_model=SchemaOrderBase)
async def edit_order(
        order_id: UUID,
        data: SchemaOrderPatch,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("product"))
):
    return await update_one_order(access=access, data=data, session=session, order_id=order_id)


@router.delete("/{id}", summary="Delete order", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
        order_id: UUID,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("product")),
):
    await delete_one_order(access=access, session=session, order_id=order_id)
    return
