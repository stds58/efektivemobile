from datetime import datetime, timedelta, timezone
import jwt
from uuid import UUID
import structlog
from pydantic import ValidationError
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.exceptions.base import (
    BlacklistedError,
    TokenExpiredError,
    BadCredentialsError,
    InvalidTokenError
)
from app.core.blacklist import token_blacklist
from app.schemas.token import AccessToken, RefreshToken


logger = structlog.get_logger()


class AuthService:
    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return await verify_password(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return get_password_hash(password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> AccessToken:
        if not token:
            logger.error("Not authenticated", error="Has no token")
            raise BadCredentialsError
        try:
            if token in token_blacklist:
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

    @staticmethod
    def ban_token(token: str):
        """Добавить токен в чёрный список"""
        token_blacklist[token] = True

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            hours=settings.REFRESH_TOKEN_EXPIRE_HOURS
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_refresh_token(token: str) -> RefreshToken:
        try:
            if token in token_blacklist:
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
