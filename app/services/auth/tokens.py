from datetime import datetime, timedelta, timezone
import jwt
from uuid import UUID
import structlog
from pydantic import ValidationError
from app.core.config import settings
from app.exceptions.base import (
    BlacklistedError,
    TokenExpiredError,
    BadCredentialsError,
    InvalidTokenError
)
from app.services.auth.blacklist import token_blacklist
from app.schemas.token import AccessToken, RefreshToken


logger = structlog.get_logger()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.utcnow(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    try:
        to_encode = data.copy()
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
    except Exception:
        raise InvalidTokenError
    return encoded_jwt


async def decode_access_token(token: str) -> AccessToken:
    if not token:
        logger.error("Not authenticated", error="Has no token")
        raise BadCredentialsError
    try:
        if await token_blacklist.is_banned(token):
            logger.error("BlacklistedError")
            raise BlacklistedError
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = UUID(payload.get("sub"))
        return AccessToken(**payload)
    except jwt.ExpiredSignatureError as exc:
        logger.info("Token expired", error=str(exc))
        raise TokenExpiredError
    except jwt.PyJWTError as exc:
        logger.error("Invalid or malformed JWT", error=str(exc))
        raise InvalidTokenError from exc
    except ValidationError as e:
        logger.error(
            "Invalid token structure", error=str(e), user_id=user_id, data=token
        )
        raise BadCredentialsError from e


def create_refresh_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            hours=settings.REFRESH_TOKEN_EXPIRE_HOURS
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception:
        raise InvalidTokenError


async def decode_refresh_token(token: str) -> RefreshToken:
    try:
        if await token_blacklist.is_banned(token):
            logger.error("BlacklistedError")
            raise BlacklistedError
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            logger.error("jwt.InvalidTokenError", error="Is not a refresh token")
            raise jwt.InvalidTokenError("Not a refresh token")
        return RefreshToken(**payload)
    except jwt.ExpiredSignatureError as exc:
        logger.info("Refresh token expired", error=str(exc))
        raise TokenExpiredError(custom_detail="Refresh token expired")
    except jwt.PyJWTError as exc:
        logger.error("Invalid or malformed JWT", error=str(exc))
        raise InvalidTokenError from exc
