import logging
import structlog
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_logging_middleware import auth_logging_middleware
from app.api.v1.base_router import v1_router
from app.api.swagger_auth.auth import swagger_router
from app.core.config import settings
from app.core.structlog_configure import configure_logging


# Подавляем логи Uvicorn (оставляем только ошибки или полностью отключаем)
if not settings.DEBUG:
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


configure_logging()
logger = structlog.get_logger()


app = FastAPI(
    debug=settings.DEBUG,
    title="API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY, max_age=3600
)

app.middleware("http")(auth_logging_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "DELETE",
        "PATCH",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)

# Включить метрики
#Теперь будет эндпоинт: http://fastapi-app:8000/metrics
Instrumentator().instrument(app).expose(app)

app.include_router(v1_router)
app.include_router(swagger_router)


@app.get("/")
def root():
    return {"message": "Auth System is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
