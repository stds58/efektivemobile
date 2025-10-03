from fastapi import APIRouter, Depends, status, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
from app.schemas.token import Token
from app.services.user import create_user, authenticate_user_api, refresh_user_tokens, set_token_in_cookie
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
        response: Response,
        session: AsyncSession = Depends(connection())
) -> Token:
    tokens = await authenticate_user_api(user_in=form_data, session=session)
    await set_token_in_cookie(response=response, tokens=tokens)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
        response: Response,
        refresh_token: str = Body(..., embed=True),
        session: AsyncSession = Depends(connection())
) -> Token:
    tokens = await refresh_user_tokens(refresh_token=refresh_token, session=session)
    await set_token_in_cookie(response=response, tokens=tokens)
    return tokens
