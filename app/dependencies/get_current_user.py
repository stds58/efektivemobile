from typing import Annotated
from uuid import uuid4
import jwt
import structlog
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError
from app.services.auth.blacklist import token_blacklist
from app.core.config import settings
from app.models.user import User
from app.services.user import get_user_by_id
from app.schemas.permission import AccessContext
from app.dependencies.get_db import connection
from app.exceptions.base import BadCredentialsError, UserInactiveError, BlacklistedError


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(connection()),
) -> User:
    try:
        if await token_blacklist.is_banned(token):
            raise BlacklistedError
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise BadCredentialsError
    except InvalidTokenError as exc:
        raise BadCredentialsError from exc

    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_id(access=access, user_id=user_id, session=session)
    if user is None:
        raise BadCredentialsError
    if not user.is_active:
        raise UserInactiveError
    return user
