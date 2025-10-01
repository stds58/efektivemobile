from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user import UserService
from app.dependencies.get_db import connection


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")

swagger_router = APIRouter(prefix="/auth", tags=["auth"])

@swagger_router.post("/swaggerlogin", response_model=Token)
async def swaggerlogin_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(connection()),
) -> Token:
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    user_roles = await user_service.get_user_roles(user_id=user.id)
    role_names = [role.name for role in user_roles]
    access_token = AuthService.create_access_token(data={"sub": str(user.id), "role": role_names})
    return Token(access_token=access_token, token_type="bearer")


@swagger_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    # JWT токены stateless. Выход реализуется на клиенте путем удаления токена.
    # На сервере можно добавить токен в черный список, если реализована такая логика.
    AuthService.ban_token(token)
    return {"message": "You have been logged out"}
