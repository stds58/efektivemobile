import structlog
from typing import Optional, AsyncGenerator, Annotated
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import create_session_factory, get_session_with_isolation
from app.exceptions.base import (
    IntegrityErrorException,
    CustomInternalServerException,
    SqlalchemyErrorException,
    DatabaseConnectionException,
)
from app.schemas.permission import RequestContext
from app.dependencies.get_payload_from_jwt import get_payload_from_jwt
from fastapi.security import OAuth2PasswordBearer


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")
async_session_maker = create_session_factory(settings.DATABASE_URL)


#auth_db_context
# Лучше использовать enum или строгие константы:
# from enum import Enum
# class BusinessDomain(str, Enum):
#     PRODUCT = "product"
#     ORDER = "order"
#     USER = "user"

# Рассмотри возможность отделять зависимости для чтения и записи:
# read_context = auth_db_context(isolation_level="READ_COMMITTED", commit=False)
# write_context = auth_db_context(isolation_level="SERIALIZABLE", commit=True)



def auth_db_context(business_element: Optional[str] = None, isolation_level: Optional[str] = "READ COMMITTED", commit: bool = True):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    """

    async def dependency(token: str = Depends(oauth2_scheme), )  -> AsyncGenerator[RequestContext, None]:
        async with get_session_with_isolation(
            async_session_maker, isolation_level
        ) as session:
            try:
                access = await get_payload_from_jwt(token=token, business_element=business_element, session=session)
                yield RequestContext(session=session, access=access)
                if commit and session.in_transaction():
                    await session.commit()
            except IntegrityError as exc:
                logger.critical("IntegrityError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise IntegrityErrorException from exc
            except OperationalError as exc:
                logger.critical("OperationalError", error=str(exc))
                raise DatabaseConnectionException from exc
            except (ConnectionRefusedError, OSError) as exc:
                logger.critical("ConnectionRefusedError, OSError", error=str(exc))
                raise CustomInternalServerException from exc
            except SQLAlchemyError as exc:
                logger.critical(" SQLAlchemyError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise SqlalchemyErrorException from exc
            except Exception as exc:
                logger.critical("Other exception", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency



def connection(isolation_level: Optional[str] = "READ COMMITTED", commit: bool = True):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    """

    async def dependency()  -> AsyncGenerator[AsyncSession, None]:
        async with get_session_with_isolation(
            async_session_maker, isolation_level
        ) as session:
            try:
                yield session
                if commit and session.in_transaction():
                    await session.commit()
            except IntegrityError as exc:
                logger.critical("IntegrityError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise IntegrityErrorException from exc
            except OperationalError as exc:
                logger.critical("OperationalError", error=str(exc))
                raise DatabaseConnectionException from exc
            except (ConnectionRefusedError, OSError) as exc:
                logger.critical("ConnectionRefusedError, OSError", error=str(exc))
                raise CustomInternalServerException from exc
            except SQLAlchemyError as exc:
                logger.critical(" SQLAlchemyError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise SqlalchemyErrorException from exc
            except Exception as exc:
                logger.critical("Other exception", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency


