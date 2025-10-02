from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user import authenticate_user
from app.dependencies.get_db import connection


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")

swagger_router = APIRouter(prefix="/auth", tags=["auth"])

@swagger_router.post("/swaggerlogin", response_model=Token)
async def swaggerlogin_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(connection()),
) -> Token:
    return await authenticate_user(user_in=form_data, session=session)


@swagger_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    # JWT токены stateless. Выход реализуется на клиенте путем удаления токена.
    # На сервере можно добавить токен в черный список, если реализована такая логика.
    AuthService.ban_token(token)
    return {"message": "You have been logged out"}
