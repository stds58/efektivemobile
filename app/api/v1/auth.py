from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user import UserService
from app.dependencies.get_db import connection


router = APIRouter()


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
    user_service = UserService(db)
    user = await user_service.authenticate_user(form_data.email, form_data.password)
    user_roles = await user_service.get_user_roles(user_id=user.id)
    role_names = [role.name for role in user_roles]
    access_token = AuthService.create_access_token(data={"sub": str(user.id), "role": role_names})
    return Token(access_token=access_token, token_type="bearer")
