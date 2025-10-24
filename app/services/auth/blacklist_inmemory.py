from abc import ABC, abstractmethod
from cachetools import TTLCache
from app.core.config import settings


TTL = (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60) + 60


class TokenBlacklist(ABC):
    @abstractmethod
    async def ban(self, token: str) -> None:
        ...

    @abstractmethod
    async def is_banned(self, token: str) -> bool:
        ...


class InMemoryTokenBlacklist(TokenBlacklist):
    def __init__(self):
        self._store = TTLCache(maxsize=10000, ttl=TTL)

    async def ban(self, token: str) -> None:
        # Добавить токен в чёрный список
        # TTLCache сам удалит запись через ttl
        self._store[token] = True

    async def is_banned(self, token: str) -> bool:
        if token in self._store:
            return True
        return False
