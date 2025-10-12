from datetime import datetime, timedelta, timezone
import jwt
import structlog
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.exceptions.base import BlacklistedError, TokenExpiredError
from app.core.blacklist import token_blacklist
from app.schemas.token import AccessToken, RefreshToken


logger = structlog.get_logger()


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

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
        try:
            if token in token_blacklist:
                logger.error("BlacklistedError")
                raise BlacklistedError
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return AccessToken(**payload)
        except jwt.PyJWTError as exc:
            logger.error("jwt.PyJWTError", error=str(exc))
            raise TokenExpiredError from exc

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
        except jwt.PyJWTError as exc:
            logger.error("jwt.PyJWTError", error=str(exc))
            raise TokenExpiredError from exc
