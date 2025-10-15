from uuid import uuid4
import structlog
from fastapi import APIRouter, Depends, status, Cookie, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.permission import AccessContext
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
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
    logger.debug("Register user", filters=filters)
    user = await create_user(user_in=user_in, session=session)
    logger.info("Registered user", filters=filters, user_id=user.id)
    return user


@router.post("/login")
async def login_for_access_token(
    form_data: SchemaUserLogin,
    response: Response,
    session: AsyncSession = Depends(connection()),
) -> dict:
    filters = SchemaUserLogin(email=form_data.email, password="*****")
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_email(
        access=access, email=form_data.email, session=session
    )

    logger.debug("Login user", user_id=user.id, filters=filters)
    tokens = await authenticate_user_api(user_in=form_data, session=session)
    logger.info("Logined user", user_id=user.id, filters=filters)

    message = await set_token_in_cookie(response=response, tokens=tokens)
    logger.info("Set token in cookie", user_id=user.id)
    return message


@router.post("/logout")
async def logout(
        response: Response,
        access_token: str = Cookie(None, alias="access_token"),
        refresh_token: str = Cookie(None, alias="refresh_token"),
) -> dict:
    payload = AuthService.decode_access_token(token=access_token)
    user_id = payload.sub

    if access_token:
        AuthService.ban_token(access_token)
        logger.info("Logouted user: baned access token", user_id=user_id)
    if refresh_token:
        AuthService.ban_token(refresh_token)
        logger.info("Logouted user: baned refresh token", user_id=user_id)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    message = {"message": "You have been logged out"}
    return message


@router.post("/refresh")
async def refresh_token_endpoint(
    response: Response,
    refresh_token: str = Cookie(None, alias="refresh_token"),
    session: AsyncSession = Depends(connection()),
) -> dict:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = AuthService.decode_refresh_token(token=refresh_token)
    user_id = payload.sub

    logger.debug("Refresh token", user_id=user_id)
    tokens = await refresh_user_tokens(refresh_token=refresh_token, session=session)
    logger.info("Refreshed token", user_id=user_id)

    logger.debug("Ban old refresh token", user_id=user_id)
    AuthService.ban_token(refresh_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    logger.info("Baned old refresh token. deleted cookie", user_id=user_id)

    message = await set_token_in_cookie(response=response, tokens=tokens)
    logger.info("Seted tokens in cookie", user_id=user_id)

    return message