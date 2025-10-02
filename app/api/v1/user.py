from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserPatch, SchemaUserFilter, SchemaUserBase
from app.services.user import find_many_user, update_user, soft_delete_user
from app.dependencies.get_db import connection
from app.dependencies.permissions import require_permission
from app.schemas.permission import AccessContext
from app.schemas.base import PaginationParams


router = APIRouter()


@router.get("", summary="Get users", response_model=List[SchemaUserBase])
async def get_users(
        filters: SchemaUserFilter = Depends(),
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("user")),
        pagination: PaginationParams = Depends(),
):
    return await find_many_user(access=access, filters=filters, session=session, pagination=pagination)


@router.patch("/{id}", summary="Update user", response_model=SchemaUserBase)
async def edit_user(
        user_id: UUID,
        user_in: SchemaUserPatch,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("user")),
):
    updated_user = await update_user(access=access, filters=user_in, session=session, user_id=user_id)
    return updated_user


@router.delete("/{id}", summary="Soft delete user", status_code=status.HTTP_204_NO_CONTENT)
async def unactivate_user(
        user_id: UUID,
        session: AsyncSession = Depends(connection()),
        access: AccessContext = Depends(require_permission("user")),
):
    await soft_delete_user(access=access, session=session, user_id=user_id)
    return
