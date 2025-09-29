from typing import Optional, AsyncGenerator
import logging
#from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import create_session_factory, get_session_with_isolation


logger = logging.getLogger(__name__)


async_session_maker = create_session_factory(settings.DATABASE_URL)


def connection(isolation_level: Optional[str] = None, commit: bool = True):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    """

    async def dependency() -> AsyncGenerator[AsyncSession, None]:
        async with get_session_with_isolation(async_session_maker, isolation_level) as session:
            try:
                #result = await session.execute(text("SHOW transaction_isolation;"))
                #print("SHOW transaction_isolation;", result.scalar())
                yield session
                if commit and session.in_transaction():
                    await session.commit()
            except IntegrityError as e:
                print('IntegrityError', e)
                logger.critical("IntegrityError: %s", e)
                if session.in_transaction():
                    await session.rollback()
                await session.rollback()
                raise e
            except OperationalError as e:
                print('OperationalError', e)
                logger.critical("OperationalError: %s", e)
                raise e
            except (ConnectionRefusedError, OSError) as e:
                print('ConnectionRefusedError', e)
                logger.critical("ConnectionRefusedError, OSError: %s", e)
                raise e
            except SQLAlchemyError as e:
                print('SQLAlchemyError', e)
                logger.critical(" SQLAlchemyError: %s", e)
                if session.in_transaction():
                    await session.rollback()
                raise e
            except Exception as e:
                print('Exception', e)
                logger.critical(" Exception: %s", e)
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency
