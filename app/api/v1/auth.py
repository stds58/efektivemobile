from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user import UserService
from app.dependencies.get_db import connection


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: SchemaUserCreate, db: AsyncSession = Depends(connection())
):
    user_service = UserService(db)
    user = await user_service.create_user(user_in)
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: SchemaUserLogin, db: AsyncSession = Depends(connection())
) -> Token:
    # Note: В реальном приложении для логина используется отдельная схема с email и password, а не UserCreate.
    # Для простоты примера используем UserCreate, но это неправильно.
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.email, form_data.password)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/swaggerlogin", response_model=Token)
async def swaggerlogin_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(connection()),
) -> Token:
    # Note: В реальном приложении для логина используется отдельная схема с email и password, а не UserCreate.
    # Для простоты примера используем UserCreate, но это неправильно.
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    # JWT токены stateless. Выход реализуется на клиенте путем удаления токена.
    # На сервере можно добавить токен в черный список, если реализована такая логика.
    AuthService.ban_token(token)
    return {"message": "You have been logged out"}
