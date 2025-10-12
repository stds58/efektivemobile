import logging
from typing import Callable, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


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
    detail = "Permission denied"


class VerifyHashError(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"


class MultipleResultsError(CustomHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Multiple rows were found when one or none was required"


class PasswordMismatchError(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Password and confirmation do not match"


class CustomInternalServerException(CustomHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка сервера"
    log_func = logger.error


class MissingLoginCredentialsException(CustomInternalServerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Either email or username must be provided"


class IntegrityErrorException(CustomInternalServerException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Нарушение целостности данных"


class ObjectsNotFoundByIDError(CustomInternalServerException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Запрашиваемый объект не найден"


class DatabaseConnectionException(CustomHTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Сервис базы данных временно недоступен"


class SerializationFailureException(CustomHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Serialization failure (40001), should retry transaction"


class SqlalchemyErrorException(CustomInternalServerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка базы данных"
