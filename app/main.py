from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as users_router
from app.core.config import settings
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    debug=settings.DEBUG,
    title="API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY, max_age=3600)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
    ],
    # добавить X-Requested-With если нужна совместимость с jQuery / устаревшими клиентами
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)



app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "Auth System is running"}




if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
