from uuid import uuid4
import structlog
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.permission import AccessContext
from app.schemas.token import Token
from app.schemas.user import SchemaUserLogin
from app.services.auth_service import AuthService
from app.services.user import authenticate_user_swagger, get_user_by_email
from app.dependencies.get_db import connection


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")

swagger_router = APIRouter(prefix="/auth", tags=["auth"])


@swagger_router.post("/swaggerlogin", response_model=Token)
async def swaggerlogin_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(connection(isolation_level="READ COMMITTED")),
) -> Token:
    filters = SchemaUserLogin(email=form_data.username, password="*****")
    fake_uuid = uuid4()
    access = AccessContext(user_id=fake_uuid, permissions=["read_all_permission"])
    user = await get_user_by_email(
        access=access, email=form_data.username, session=session
    )

    logger.info("Login swagger user", user_id=user.id, filters=filters)
    obj = await authenticate_user_swagger(user_in=form_data, session=session)
    logger.info("Logined swagger user", user_id=user.id, filters=filters)

    return obj


@swagger_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> dict:
    AuthService.ban_token(token)
    return {"message": "You have been logged out"}
