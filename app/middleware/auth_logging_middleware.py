import time
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from fastapi import Request


logger = structlog.get_logger()


def get_client_ip(request: Request) -> str:
    if forwarded := request.headers.get("x-forwarded-for"):
        return forwarded.split(",")[0].strip()
    if real_ip := request.headers.get("x-real-ip"):
        return real_ip
    return request.client.host if request.client else "unknown"


async def auth_logging_middleware(request: Request, call_next):
    clear_contextvars()

    ip = get_client_ip(request)
    bind_contextvars(ip=ip)
    bind_contextvars(method=request.method)
    bind_contextvars(path=request.url.path)
    bind_contextvars(user_agent=request.headers.get("user-agent"))

    response = await call_next(request)

    return response
