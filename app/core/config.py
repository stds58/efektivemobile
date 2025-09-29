"""
Класс настроек приложения
"""
import secrets
from cachetools import TTLCache
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


load_dotenv()


class Settings(BaseSettings):
    """
    берёт настройки из .env-а
    """

    APP_NAME: str
    ENVIRONMENT: str
    DEBUG: bool
    SECRET_KEY: str = Field(default_factory=lambda: Settings._generate_secret_key())
    SESSION_MIDDLEWARE_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_HOURS: int
    ALGORITHM: str

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT_EXTERNAL: int
    DB_PORT_INTERNAL: int

    @property
    def DATABASE_URL(self) -> str:  # pylint: disable=invalid-name
        return (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT_EXTERNAL}/{settings.DB_NAME}"
        )

    @staticmethod
    def _generate_secret_key() -> str:
        return secrets.token_urlsafe(64)


    model_config = ConfigDict(extra="ignore")


@lru_cache()
def get_settings():
    """
    кеширует экземпляр объекта настроек Settings, чтобы избежать повторной инициализации
    """
    return Settings()


settings = get_settings()
