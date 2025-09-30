from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserPatch, UserPublic
from app.services.user import UserService
from app.dependencies.get_db import connection
from app.dependencies.get_current_user import get_current_user
from app.models.user import User
from app.dependencies.permissions import require_permission


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_user)],
        db: AsyncSession = Depends(connection())
):
    #user_service = UserService(db)
    #roles = await user_service.get_user_roles(user_id=current_user.id)
    #current_user.role = [role.name for role in roles]
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    user_in: SchemaUserPatch,
    db: AsyncSession = Depends(connection()),
    current_user: User = Depends(require_permission("user", "update_permission")),
):
    user_service = UserService(db)
    updated_user = await user_service.update_user(str(current_user.id), user_in)
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    db: AsyncSession = Depends(connection()),
    current_user: User = Depends(require_permission("user", "delete_permission")),
):
    user_service = UserService(db)
    success = await user_service.soft_delete_user(str(current_user.id))
    return
