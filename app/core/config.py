"""
Класс настроек приложения
"""
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


load_dotenv()


class Settings(BaseSettings):
    """
    берёт настройки из .env-а
    """
    APP_NAME: str
    DEBUG: bool
    SECRET_KEY: str
    SESSION_MIDDLEWARE_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
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

    model_config = ConfigDict(extra="ignore")


@lru_cache()
def get_settings():
    """
    кеширует экземпляр объекта настроек Settings, чтобы избежать повторной инициализации
    """
    return Settings()


settings = get_settings()
