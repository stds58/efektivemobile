from uuid import UUID
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserCreate, SchemaUserPatch, UserPublic, SchemaUserFilter, SchemaUserBase
from app.services.user import UserService, find_many_user, update_user
from app.dependencies.get_db import connection
from app.dependencies.get_current_user import get_current_user
from app.models.user import User
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
async def edit_users(
        id: UUID,
        user_in: SchemaUserPatch,
        session: AsyncSession = Depends(connection()),
        #current_user: User = Depends(require_permission("user")),
):
    print('user_in', user_in)
    updated_user = await update_user(filters=user_in, session=session, user_id=id)
    return updated_user


@router.get("/me", response_model=UserPublic)
async def read_users_me(
        #current_user: User = Depends(require_permission("user", "read_permission")),
        current_user: User = Depends(require_permission("user")),
        #current_user: Annotated[User, Depends(get_current_user)],
        #db: AsyncSession = Depends(connection())
):
    #user_service = UserService(db)
    #roles = await user_service.get_user_roles(user_id=current_user.id)
    #current_user.role = [role.name for role in roles]
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    user_in: SchemaUserPatch,
    db: AsyncSession = Depends(connection()),
    #current_user: User = Depends(require_permission("user", "update_permission")),
    current_user: User = Depends(require_permission("user")),
):
    user_service = UserService(db)
    updated_user = await user_service.update_user(str(current_user.id), user_in)
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    db: AsyncSession = Depends(connection()),
    #current_user: User = Depends(require_permission("user", "delete_permission")),
    current_user: User = Depends(require_permission("user")),
):
    user_service = UserService(db)
    success = await user_service.soft_delete_user(str(current_user.id))
    return
