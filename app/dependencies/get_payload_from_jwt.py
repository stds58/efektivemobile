import structlog
from typing import Annotated, List
from uuid import UUID, uuid4
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import AuthService
from app.schemas.permission import AccessContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user import get_user_by_id, ensureUserIsActive
from app.crud.user import UserDAO


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_user_id_from_jwt(
    token: str,
    session: AsyncSession,
) -> UUID:
    payload = AuthService.decode_access_token(token=token)
    user_id = payload.sub
    await ensureUserIsActive(user_id=user_id, session=session)
    return user_id


def get_roles_from_jwt(
    token: str,
) -> List[str]:
    payload = AuthService.decode_access_token(token=token)
    list_permissions = payload.role
    return list_permissions


async def get_payload_from_jwt(token: str, business_element: str, session: AsyncSession):
    user_id = await get_user_id_from_jwt(token=token, session=session)
    list_permissions = await UserDAO.get_with_permissions(
        user_id=user_id,
        business_element_name=business_element,
        session=session,
    )
    return AccessContext(user_id=user_id, permissions=list_permissions)
