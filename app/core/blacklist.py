from cachetools import TTLCache
from app.core.config import settings


TTL = (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60) + 60
token_blacklist = TTLCache(maxsize=10000, ttl=TTL)
