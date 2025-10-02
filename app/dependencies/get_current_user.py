from typing import Annotated
from uuid import uuid4
import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from app.services.user import get_user_by_id
from app.dependencies.get_db import connection
from app.models.user import User
#from app.schemas.token import TokenData
from app.exceptions.base import BadCredentialsError, UserInactiveError, BlacklistedError
from app.core.blacklist import token_blacklist
from app.schemas.permission import AccessContext


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(connection()),
) -> User:
    try:
        if token in token_blacklist:
            raise BlacklistedError
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise BadCredentialsError
        #token_data = TokenData(user_id=user_id)
    except InvalidTokenError as exc:
        raise BadCredentialsError from exc

    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_id(access=access, user_id=user_id, session=db)
    if user is None:
        raise BadCredentialsError
    if not user.is_active:
        raise UserInactiveError
    return user
