import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.stubs import FAKE_ACCESS_CONTEXT
from app.schemas.token import Token
from app.schemas.user import (
    SchemaUserLogin,
    SchemaUserSwaggerLogin,
    SchemaUserLoginMain,
)
from app.services.user_role import get_list_user_rolenames
from app.services.auth.tokens import create_access_token, create_refresh_token
from app.services.auth.password import verify_password
from app.exceptions.base import (
    BadCredentialsError,
    UserInactiveError,
)
from app.services.user import get_hashed_password, get_user_by_email


logger = structlog.get_logger()


async def authenticate_user(
    user_in: SchemaUserLoginMain, session: AsyncSession
) -> Token:
    login = user_in.email if user_in.username is None else user_in.username
    user = await get_user_by_email(
        access=FAKE_ACCESS_CONTEXT, email=login, session=session
    )

    if not user:
        logger.error("в БД отсутствует user_id", user_id=user.id)
        # +1 попытка в список
        raise BadCredentialsError
    if not user.is_active:
        logger.error("пользователь отключён", user_id=user.id)
        # +1 попытка в список
        raise UserInactiveError
    hash_password = await get_hashed_password(user_id=user.id, session=session)
    if not await verify_password(user_in.password, hash_password):
        # +1 попытка в список
        raise BadCredentialsError

    role_names = await get_list_user_rolenames(
        access=FAKE_ACCESS_CONTEXT, session=session, user_id=user.id
    )

    access_token = create_access_token(data={"sub": str(user.id), "role": role_names})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token)


async def authenticate_user_api(
    user_in: SchemaUserLogin, session: AsyncSession
) -> Token:
    user = SchemaUserLoginMain(email=user_in.email, password=user_in.password)
    return await authenticate_user(user_in=user, session=session)


async def authenticate_user_swagger(
    user_in: SchemaUserSwaggerLogin, session: AsyncSession
) -> Token:
    user = SchemaUserSwaggerLogin(username=user_in.username, password=user_in.password)
    return await authenticate_user(user_in=user, session=session)
