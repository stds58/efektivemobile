import structlog
from typing import Annotated
from uuid import uuid4
import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from app.services.user import get_user_by_id
from app.dependencies.get_db import connection
from app.models.user import User
from app.exceptions.base import BadCredentialsError, UserInactiveError, BlacklistedError
from app.core.blacklist import token_blacklist
from app.schemas.permission import AccessContext


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(connection()),
) -> User:
    try:
        if token in token_blacklist:
            logger.error("Токен в чёрном списке")
            raise BlacklistedError
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            logger.error("в токене отсутствует user_id")
            raise BadCredentialsError
    except InvalidTokenError as exc:
        logger.error("Невалидный токен", error=str(exc))
        raise BadCredentialsError from exc

    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_id(access=access, user_id=user_id, session=db)
    if user is None:
        logger.error("в БД отсутствует user_id", user_id=user_id)
        raise BadCredentialsError
    if not user.is_active:
        logger.error("пользователь отключён", user_id=user_id)
        raise UserInactiveError

    #Сохраняем user_id в request.state
    request.state.user_id = user.id
    request.state.user_email = user.email

    return user
