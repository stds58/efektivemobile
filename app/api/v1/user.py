import structlog
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain, IsolationLevel
from app.schemas.user import SchemaUserPatch, SchemaUserFilter, SchemaUserBase
from app.services.user import find_many_user, update_user, soft_delete_user
from app.dependencies.get_db import connection, auth_db_context
from app.dependencies.permissions import require_permission
from app.schemas.permission import AccessContext
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext


logger = structlog.get_logger()


router = APIRouter()


@router.get("", summary="Get users", response_model=List[SchemaUserBase])
async def get_users(
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.USER,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=False
        )
    ),
    filters: SchemaUserFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    user = await find_many_user(
        business_element=BusinessDomain.USER,
        session=request_context.session,
        access=request_context.access,
        filters=filters,
        pagination=pagination,
    )
    logger.info("Get users", filters=filters, pagination=pagination)
    return user


@router.patch("/{id}", summary="Update user", response_model=SchemaUserBase)
async def edit_user(
    user_id: UUID,
    user_in: SchemaUserPatch,
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("user")),
):
    updated_user = await update_user(
        access=access, filters=user_in, session=session, user_id=user_id
    )
    return updated_user


@router.delete(
    "/{id}", summary="Soft delete user", status_code=status.HTTP_204_NO_CONTENT
)
async def unactivate_user(
    user_id: UUID,
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("user")),
):
    await soft_delete_user(access=access, session=session, user_id=user_id)
    return
