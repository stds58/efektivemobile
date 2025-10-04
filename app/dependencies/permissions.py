from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import connection
from app.models.user import User
from app.crud.user import UserDAO
from app.schemas.permission import AccessContext


def require_permission(business_element: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(connection()),
    ) -> AccessContext:
        list_permissions = await UserDAO.get_with_permissions(
            user_id=current_user.id,
            business_element_name=business_element,
            session=session,
        )

        return AccessContext(user_id=current_user.id, permissions=list_permissions)

    return dependency
