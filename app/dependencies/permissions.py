from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import connection
from app.services.user import UserService
from app.models.user import User
from app.exceptions.base import PermissionDenied
from app.schemas.permission import AccessContext


def require_permission(business_element: str):
    async def dependency(
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(connection()),
    ) -> AccessContext:
        user_service = UserService(db)

        list_permissions = await user_service.get_user_permission(user_id=current_user.id, business_element_name=business_element)
        return AccessContext(
            user_id=current_user.id,
            permissions=list_permissions
        )

    return dependency
