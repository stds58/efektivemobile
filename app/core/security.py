from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import structlog
from app.core.config import settings
from app.exceptions.base import VerifyHashError


logger = structlog.get_logger()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except ValueError as exc:
        logger.error("ValueError", error=str(exc))
        raise VerifyHashError from exc
    except TypeError as exc:
        logger.error("TypeError", error=str(exc))
        raise VerifyHashError from exc


def get_password_hash(password: str) -> str:
    try:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")
    except ValueError as exc:
        logger.error("ValueError", error=str(exc))
        raise VerifyHashError from exc
    except TypeError as exc:
        logger.error("TypeError", error=str(exc))
        raise VerifyHashError from exc


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
