"""
Контекстный менеджер для создания сессии с опциональным уровнем изоляции.
Для гибкого управления уровнем изоляции
"""

from typing import Optional
import asyncio
from contextlib import asynccontextmanager
import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


logger = structlog.get_logger()


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
            # logger.info("Текущий уровень изоляции", isolation_level=isolation_level)
            yield session
    except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as exc:
        logger.error(
            "Ошибка (ConnectionRefusedError, OSError, asyncio.TimeoutError)",
            error=str(exc),
        )
        raise
