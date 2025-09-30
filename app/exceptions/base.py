import logging
from typing import Callable, Optional
import socket
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse


logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"
    log_func: Callable = logging.error

    def __init__(self, custom_detail: Optional[str] = None) -> None:
        final_detail = custom_detail if custom_detail is not None else self.detail
        super().__init__(status_code=self.status_code, detail=final_detail)

    async def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        self.log_func("%s: %s", self.detail, exception)
        return JSONResponse(
            content={"message": self.detail},
            status_code=self.status_code,
        )


class HttpExceptionHandler(Exception):
    async def __call__(
        self, request: Request, exception: HTTPException
    ) -> JSONResponse | RedirectResponse:
        if exception.headers and "Location" in exception.headers:
            return RedirectResponse(
                url=exception.headers["Location"], status_code=exception.status_code
            )
        return JSONResponse(
            status_code=exception.status_code,
            content={"error": exception.detail},
        )


class BadCredentialsError(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid credentials"


class EmailAlreadyRegisteredError(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Check your inbox - if an account exists, you’ll receive an email"


class UserInactiveError(CustomHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Check your inbox for activate"


class BlacklistedError(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Your token has been revoked"


class TokenExpiredError(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"


class PermissionDenied(CustomHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied"


class CustomNotFoundException(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Ресурс не найден"


class CustomBadRequestException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Неверный запрос"


class CustomInternalServerException(CustomHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка сервера"
    log_func = logger.error


class IdentityProviderException(CustomInternalServerException):
    detail = "Не удалось проверить доступ"


class TokenExpiredException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек"


class NoUserIdException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Идентификатор пользователя отсутствуе"


class ForbiddenException(CustomHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступ запрещен"


class IncorrectEmailOrPasswordException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный email или пароль"


class UserAlreadyExistsError(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Пользователь с таким email уже существует"


class RedisConnectionException(CustomInternalServerException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Сервис кэша временно недоступен. Попробуйте позже"


class RedisPermissionException(CustomInternalServerException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Нет прав для доступа к данным в Redis"


class RedisTimeoutException(CustomInternalServerException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Сервис кэша не отвечает"


class DatabaseConnectionException(CustomInternalServerException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Сервис базы данных временно недоступен"


class TypeErrorException(CustomInternalServerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка обработки данных сервера"


class ValueErrorException(CustomInternalServerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка сериализации данных"


class IntegrityErrorException(CustomInternalServerException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Ошибка базы данных"


class OsErrorException(CustomInternalServerException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    async def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        if isinstance(exception, socket.gaierror):
            self.detail = "Не удалось разрешить имя хоста"
        else:
            self.detail = "Системная ошибка ввода-вывода"
        return await super().__call__(request, exception)


class SqlalchemyErrorException(CustomInternalServerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка базы данных"


class SqlalchemyProgrammingException(CustomHTTPException):
    async def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        if 'relation "' in str(exception) and "does not exist" in str(exception):
            self.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            self.detail = "База данных не инициализирована: отсутствует таблица. Требуются миграции."
            self.log_func = logger.warning
        else:
            self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.detail = "SQLAlchemy ProgrammingError"
            self.log_func = logger.error
        return await super().__call__(request, exception)
