import bcrypt
from concurrent.futures import ThreadPoolExecutor
import asyncio
import structlog
from app.exceptions.base import VerifyHashError


logger = structlog.get_logger()


# Ограничьте число потоков, чтобы не создавать 1000 потоков при 1000 логинах
executor = ThreadPoolExecutor(max_workers=10)  # например, 2–4× ядра CPU


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return await asyncio.get_event_loop().run_in_executor(
            executor, bcrypt.checkpw, password_bytes, hash_bytes
        )
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
