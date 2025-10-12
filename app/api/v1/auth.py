from uuid import uuid4
import structlog
from fastapi import APIRouter, Depends, status, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.permission import AccessContext
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user import (
    create_user,
    authenticate_user_api,
    refresh_user_tokens,
    set_token_in_cookie,
    get_user_by_email,
)
from app.dependencies.get_db import connection


logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: SchemaUserCreate, session: AsyncSession = Depends(connection())
):
    filters = SchemaUserCreate(
        email=user_in.email,
        password="*****",
        password_confirm="*****",
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    logger.info("Register user", filters=filters)
    user = await create_user(user_in=user_in, session=session)
    logger.info("Registered user", filters=filters, user_id=user.id)
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: SchemaUserLogin,
    response: Response,
    session: AsyncSession = Depends(connection()),
) -> Token:
    filters = SchemaUserLogin(email=form_data.email, password="*****")
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_email(
        access=access, email=form_data.email, session=session
    )

    logger.info("Login user", user_id=user.id, filters=filters)
    tokens = await authenticate_user_api(user_in=form_data, session=session)
    logger.info("Logined user", user_id=user.id, filters=filters)

    await set_token_in_cookie(response=response, tokens=tokens)
    logger.info("Set token in cookie", user_id=user.id)
    return tokens


@router.post("/logout")
async def logout(token: str) -> dict:
    AuthService.ban_token(token)
    logger.info("Logouted user")
    return {"message": "You have been logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    response: Response,
    refresh_token: str = Body(..., embed=True),
    session: AsyncSession = Depends(connection()),
) -> Token:
    tokens = await refresh_user_tokens(refresh_token=refresh_token, session=session)
    await set_token_in_cookie(response=response, tokens=tokens)
    return tokens
