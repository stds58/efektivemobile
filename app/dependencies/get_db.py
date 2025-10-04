from typing import Optional, AsyncGenerator
import logging
# from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import create_session_factory, get_session_with_isolation
from app.exceptions.base import (
    IntegrityErrorException,
    CustomInternalServerException,
    SqlalchemyErrorException,
    DatabaseConnectionException
)


logger = logging.getLogger(__name__)


async_session_maker = create_session_factory(settings.DATABASE_URL)


def connection(isolation_level: Optional[str] = None, commit: bool = True):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    """

    async def dependency() -> AsyncGenerator[AsyncSession, None]:
        async with get_session_with_isolation(
            async_session_maker, isolation_level
        ) as session:
            try:
                # result = await session.execute(text("SHOW transaction_isolation;"))
                # print("SHOW transaction_isolation;", result.scalar())
                yield session
                if commit and session.in_transaction():
                    await session.commit()
            except IntegrityError as exc:
                logger.critical("IntegrityError: %s", exc)
                if session.in_transaction():
                    await session.rollback()
                await session.rollback()
                raise IntegrityErrorException from exc
            except OperationalError as exc:
                logger.critical("OperationalError: %s", exc)
                raise DatabaseConnectionException from exc
            except (ConnectionRefusedError, OSError) as exc:
                logger.critical("ConnectionRefusedError, OSError: %s", exc)
                raise CustomInternalServerException from exc
            except SQLAlchemyError as exc:
                logger.critical(" SQLAlchemyError: %s", exc)
                if session.in_transaction():
                    await session.rollback()
                raise SqlalchemyErrorException from exc
            except Exception as exc:
                logger.critical(" Exception: %s", exc)
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency
