from typing import List
import structlog
from fastapi import APIRouter, Depends, status, Cookie, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import SchemaUserCreate, SchemaUserLogin, UserPublic
from app.services.user import (
    create_user,
    refresh_access_token,
    set_access_token_in_cookie,
    set_refresh_token_in_cookie,
    get_user_by_email,
)
from app.services.auth.authenticate import authenticate_user_api
from app.dependencies.get_db import connection
from app.services.auth.blacklist import token_blacklist
from app.core.stubs import FAKE_ACCESS_CONTEXT
from app.services.auth.tokens import decode_access_token, decode_refresh_token

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
) -> List[dict]:
    filters = SchemaUserLogin(email=form_data.email, password="*****")
    user = await get_user_by_email(
        access=FAKE_ACCESS_CONTEXT, email=form_data.email, session=session
    )

    logger.debug("Login user", user_id=user.id, filters=filters)
    tokens = await authenticate_user_api(user_in=form_data, session=session)
    logger.info("Logined user", user_id=user.id, filters=filters)

    message_access = await set_access_token_in_cookie(
        response=response, access_token=tokens.access_token
    )
    message_refresh = await set_refresh_token_in_cookie(
        response=response, refresh_token=tokens.refresh_token
    )
    message = [message_access, message_refresh]
    logger.info("Seted tokens in cookie", user_id=user.id)
    return message


@router.post("/logout")
async def logout(
    response: Response,
    access_token: str = Cookie(None, alias="access_token"),
    refresh_token: str = Cookie(None, alias="refresh_token"),
) -> dict:
    payload = await decode_access_token(token=access_token)
    user_id = payload.sub

    if access_token:
        logger.debug("Logout user: ban access token", user_id=user_id)
        token_blacklist.ban(access_token)
        logger.info("Logouted user: baned access token", user_id=user_id)
    else:
        logger.debug("Logout user: has no access token", user_id=user_id)
    if refresh_token:
        logger.debug("Logout user: ban refresh token", user_id=user_id)
        token_blacklist.ban(refresh_token)
        logger.info("Logouted user: baned refresh token", user_id=user_id)
    else:
        logger.debug("Logout user: has no refresh token", user_id=user_id)

    response.delete_cookie("access_token")
    logger.debug("Logout user: delete old access token from cookie", user_id=user_id)
    response.delete_cookie("refresh_token")
    logger.debug("Logout user: delete old refresh token from cookie", user_id=user_id)

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

    payload = await decode_refresh_token(token=refresh_token)
    user_id = payload.sub

    logger.debug("Refresh access token", user_id=user_id)
    access_token = await refresh_access_token(
        refresh_token=refresh_token, session=session
    )
    logger.info("Refreshed access token", user_id=user_id)

    message = await set_access_token_in_cookie(
        response=response, access_token=access_token
    )
    logger.info("Seted access token in cookie", user_id=user_id)

    return message
