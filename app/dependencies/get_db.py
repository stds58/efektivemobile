from typing import Optional, AsyncGenerator
import structlog
from structlog.contextvars import bind_contextvars
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.enums import BusinessDomain, IsolationLevel
from app.db.session import create_session_factory, get_session_with_isolation
from app.exceptions.base import (
    IntegrityErrorException,
    CustomInternalServerException,
    SqlalchemyErrorException,
    DatabaseConnectionException,
    SerializationFailureException,
    BadCredentialsError,
)
from app.schemas.permission import RequestContext
from app.dependencies.get_payload_from_jwt import get_payload_from_jwt


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")
async_session_maker = create_session_factory(settings.DATABASE_URL)


async def get_token_from_either(request: Request) -> str:
    """
    Получает токен из заголовка Authorization или из куки access_token
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token

    logger.error("Not authenticated", error="Has no token")
    raise BadCredentialsError


def auth_db_context(
    business_element: Optional[BusinessDomain] = None,
    isolation_level: Optional[str] = IsolationLevel.READ_COMMITTED,
):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    Сессия и пользователь в одном контексте.
    """

    async def dependency(
        token: str = Depends(get_token_from_either),
    ) -> AsyncGenerator[RequestContext, None]:
        async with get_session_with_isolation(
            async_session_maker, isolation_level
        ) as session:
            session_id_obj = (await session.execute(text("SELECT pg_backend_pid()")))
            session_id = session_id_obj.scalar_one()
            transaction_id_obj = await session.execute(text("SELECT txid_current()"))
            transaction_id = transaction_id_obj.scalar()
            try:
                access = await get_payload_from_jwt(
                    token=token, business_element=business_element, session=session
                )

                bind_contextvars(
                    user_id=access.user_id,
                    business_element=business_element.value
                    if business_element
                    else None,
                    isolation_level=isolation_level,
                    #commit=commit,
                    session_id=session_id,
                    transaction_id=transaction_id
                )

                logger.info(
                    "Текущий уровень изоляции и коммит",
                    user_id=access.user_id,
                )
                yield RequestContext(session=session, access=access)
            except IntegrityError as exc:
                logger.error("IntegrityError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise IntegrityErrorException from exc
            except OperationalError as exc:
                # Проверяем, является ли ошибка serialization failure
                if hasattr(exc.orig, "pgcode") and exc.orig.pgcode == "40001":
                    logger.warning(
                        "Serialization failure (40001), should retry transaction"
                    )
                    if session.in_transaction():
                        await session.rollback()
                    # Но здесь нельзя просто "повторить" — нужно перезапустить ВСЮ транзакцию
                    raise SerializationFailureException from exc
                logger.error("OperationalError (non-serialization)", error=str(exc))
                raise DatabaseConnectionException from exc
            except (ConnectionRefusedError, OSError) as exc:
                logger.error("ConnectionRefusedError, OSError", error=str(exc))
                raise CustomInternalServerException from exc
            except SQLAlchemyError as exc:
                logger.error(" SQLAlchemyError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise SqlalchemyErrorException from exc
            except Exception as exc:
                logger.error("Other exception", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency


def connection(isolation_level: Optional[str] = "READ COMMITTED", commit: bool = True):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию с заданным уровнем изоляции.
    """

    async def dependency() -> AsyncGenerator[AsyncSession, None]:
        async with get_session_with_isolation(
            async_session_maker, isolation_level
        ) as session:
            try:
                yield session
                if commit and session.in_transaction():
                    await session.commit()
            except IntegrityError as exc:
                logger.error("IntegrityError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise IntegrityErrorException from exc
            except OperationalError as exc:
                logger.error("OperationalError", error=str(exc))
                raise DatabaseConnectionException from exc
            except (ConnectionRefusedError, OSError) as exc:
                logger.error("ConnectionRefusedError, OSError", error=str(exc))
                raise CustomInternalServerException from exc
            except SQLAlchemyError as exc:
                logger.error(" SQLAlchemyError", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise SqlalchemyErrorException from exc
            except Exception as exc:
                logger.error("Other exception", error=str(exc))
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency
