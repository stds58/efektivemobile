import structlog
from fastapi import Request


logger = structlog.get_logger()


def get_client_ip(request: Request) -> str:
    if forwarded := request.headers.get("x-forwarded-for"):
        return forwarded.split(",")[0].strip()
    if real_ip := request.headers.get("x-real-ip"):
        return real_ip
    return request.client.host if request.client else "unknown"

async def auth_logging_middleware(request: Request, call_next):
    response = await call_next(request)

    # Логируем ТОЛЬКО успешные авторизованные запросы (2xx, 3xx)
    if 200 <= response.status_code < 500:
        user_id = getattr(request.state, "user_id", None)
        if user_id is not None:
            ip = get_client_ip(request)
            logger.info(
                "AUTHORIZED REQUEST",
                user_id=user_id,
                ip=ip,
                method=request.method,
                path=request.url.path,
                status=response.status_code
            )

    return response
