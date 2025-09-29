import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings
from passlib.context import CryptContext
from app.schemas.user import UserInDB


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    # @staticmethod
    # def get_user(db, username: str):
    #     if username in db:
    #         user_dict = db[username]
    #         return UserInDB(**user_dict)
    #
    # @staticmethod
    # def authenticate_user(db, username: str, password: str):
    #     user = get_user(db, username)
    #     if not user:
    #         return False
    #     if not verify_password(password, user.hashed_password):
    #         return False
    #     return user
