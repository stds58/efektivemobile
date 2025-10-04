from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from app.core.config import settings
from app.exceptions.base import BlacklistedError, TokenExpiredError
from app.core.blacklist import token_blacklist
from app.exceptions.base import VerifyHashError
from app.schemas.token import Token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except UnknownHashError as exc:
            raise VerifyHashError from exc

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    # @staticmethod
    # def decode_access_token(token: str) -> Optional[dict]:
    #     try:
    #         if token in token_blacklist:
    #             raise BlacklistedError
    #         payload = jwt.decode(
    #             token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    #         )
    #         return payload
    #     except jwt.PyJWTError as exc:
    #         raise TokenExpiredError from exc

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

    # @staticmethod
    # def refresh_tokens(refresh_token: str) -> Token:
    #     """
    #     Обновляет access и refresh токены на основе действительного refresh-токена.
    #     """
    #     payload = AuthService.decode_refresh_token(refresh_token)
    #     user_id = payload.get("sub")
    #
    #     new_access_token = AuthService.create_access_token({"sub": user_id})
    #     new_refresh_token = AuthService.create_refresh_token({"sub": user_id})
    #
    #     return Token(access_token=new_access_token, refresh_token=new_refresh_token)

    @staticmethod
    def decode_refresh_token(token: str) -> Optional[dict]:
        try:
            if token in token_blacklist:
                raise BlacklistedError
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError("Not a refresh token")
            return payload
        except jwt.PyJWTError as exc:
            raise TokenExpiredError from exc
