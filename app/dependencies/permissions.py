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

        # has_read_all = await user_service.check_permission(
        #     user_id=current_user.id,
        #     business_element_name="product",
        #     permission="read_all_permission"
        # )
        #
        # if has_read_all:
        #     return SchemaProductFilter(
        #         **client_filters.model_dump()
        #     )
        # else:
        #     return SchemaProductFilter(
        #         **client_filters.model_dump()
        #         #,user_id=current_user.id
        #     )
        #
        # # Проверяем базовое разрешение
        # has_read = await user_service.check_permission(
        #     user_id=current_user.id,
        #     business_element_name="product",
        #     permission="read_permission"
        # )
        #
        # if not has_read:
        #     raise PermissionDenied(
        #         custom_detail="Missing read or read_all permission on product"
        #     )
        #
        # return AccessContext(user_id=current_user.id, can_read_all=False)

    return dependency

# def require_permission(business_element: str, permission: str):
#     """
#     Фабрика зависимостей для проверки прав доступа.
#     Пример использования:
#         Depends(require_permission("user", "update_permission"))
#     """
#
#     async def permission_checker(
#             current_user: User = Depends(get_current_user),
#             db: AsyncSession = Depends(connection()),
#     ) -> User:
#         user_service = UserService(db)
#         has_access = await user_service.check_permission(
#             user_id=current_user.id,
#             business_element_name=business_element,
#             permission=permission
#         )
#         if not has_access:
#             raise PermissionDenied(custom_detail="Missing permission: %s on %s" % (permission, business_element))
#         return current_user
#
#     return permission_checker
