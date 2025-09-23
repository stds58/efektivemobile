from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import SchemaUserCreate, SchemaUserBase, SchemaUserPatch, SchemaUserLogin, UserPublic, UserInDB
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user import UserService
from app.dependencies.get_db import connection
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from datetime import datetime, timedelta, timezone



router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: SchemaUserCreate, db: AsyncSession = Depends(connection())):
    user_service = UserService(db)
    try:
        user = await user_service.create_user(user_in)
        print('user == ',user)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: SchemaUserLogin, db: AsyncSession = Depends(connection())) -> Token:
    # Note: В реальном приложении для логина используется отдельная схема с email и password, а не UserCreate.
    # Для простоты примера используем UserCreate, но это неправильно.
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/swaggerlogin", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(connection())
) -> Token:
    # Note: В реальном приложении для логина используется отдельная схема с email и password, а не UserCreate.
    # Для простоты примера используем UserCreate, но это неправильно.
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(connection())):
    # JWT токены stateless. Выход реализуется на клиенте путем удаления токена.
    # На сервере можно добавить токен в черный список, если реализована такая логика.
    return
