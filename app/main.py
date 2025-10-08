import structlog
from structlog.processors import CallsiteParameterAdder, CallsiteParameter
import logging
import sys
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_logging_middleware import auth_logging_middleware
from app.api.v1.base_router import v1_router
from app.api.swagger_auth.auth import swagger_router
from app.core.config import settings
from app.utils.importer_data import seed_all


logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracebacks,
        CallsiteParameterAdder(
            [
                CallsiteParameter.FILENAME,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            ]
        ),
        structlog.processors.JSONRenderer(ensure_ascii=False),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "development":
        await seed_all()
    yield


app = FastAPI(
    debug=settings.DEBUG,
    lifespan=lifespan,
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




app.include_router(v1_router)
app.include_router(swagger_router)


@app.get("/")
def root():
    return {"message": "Auth System is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
