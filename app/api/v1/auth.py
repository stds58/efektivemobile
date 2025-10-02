from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
from app.schemas.token import Token
from app.services.user import create_user, authenticate_user
from app.dependencies.get_db import connection


router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_in: SchemaUserCreate,
        session: AsyncSession = Depends(connection())
):
    user = await create_user(user_in=user_in, session=session)
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: SchemaUserLogin,
        session: AsyncSession = Depends(connection())
) -> Token:
    return await authenticate_user(user_in=form_data, session=session)
