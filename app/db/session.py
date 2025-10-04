"""
Контекстный менеджер для создания сессии с опциональным уровнем изоляции.
Для гибкого управления уровнем изоляции
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional
import asyncio
from fastapi import HTTPException as FastAPIHTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.exceptions import HTTPException as StarletteHTTPException


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session_factory(database_url: str):
    """Создает фабрику сессий для заданного URL базы данных"""
    engine = create_async_engine(database_url)
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session_with_isolation(
    session_factory, isolation_level: Optional[str] = None
):
    try:
        async with session_factory() as session:
            if isolation_level:
                await session.connection(
                    execution_options={"isolation_level": isolation_level}
                )
                # Проверяем уровень изоляции
                result = await session.execute(
                    text("SHOW TRANSACTION ISOLATION LEVEL;")
                )
                current_isolation_level = result.scalar()
                logger.info("Текущий уровень изоляции: %s", current_isolation_level)
            yield session
    except (FastAPIHTTPException, StarletteHTTPException) as exc:
        logger.error("Ошибка подключения к БД при создании сессии: %s", exc)
        raise
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as exc:
        logger.error("Ошибка подключения к БД при создании сессии %s", exc)
        raise
    except Exception as exc:
        logger.error("Неожиданная ошибка при создании сессии: %s", exc)
        raise
