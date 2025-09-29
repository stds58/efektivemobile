from typing import Optional, Annotated
import jwt
from fastapi import Depends, HTTPException, status
from app.services.auth_service import AuthService
from app.services.user import UserService
from app.dependencies.get_db import connection
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from app.core.config import settings
from app.schemas.token import TokenData
from app.crud.user import CRUDUser
from app.exceptions.base import BadCredentialsError, EmailAlreadyRegisteredError, UserInactiveError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(connection())
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise BadCredentialsError
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise BadCredentialsError

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id=token_data.user_id)
    if user is None:
        raise BadCredentialsError
    if not user.is_active:
        raise UserInactiveError
    return user

#UserInactiveError
