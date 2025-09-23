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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(connection())
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print('payload  ',payload)
        user_id = payload.get("sub")
        print('user_id', user_id)
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id=token_data.user_id)
    print('user', user)
    if user is None:
        raise credentials_exception
    return user

