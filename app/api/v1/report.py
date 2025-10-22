from uuid import UUID
from fastapi import Request
from pathlib import Path
import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.private_router import private_route_dependency
from app.services.report import get_report
from app.schemas.permission import RequestContext
from app.dependencies.get_db import auth_db_context


logger = structlog.get_logger()

V2_DIR = Path(__file__).resolve().parent
API_DIR = V2_DIR.parent
APP_DIR = API_DIR.parent
TEMPLATES_DIR = APP_DIR / "templates"

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/{file_upload_id}/generate-report")
async def generate_report(
    file_upload_id: UUID,
    extension: str,
    sheet_name: str,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.FILE_UPLOAD,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Get content", model_id=file_upload_id)
    content = await get_report(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        session=request_context.session,
        file_upload_id=file_upload_id,
        extension=extension,
        sheet_name=sheet_name,
    )
    logger.info("Geted content", model_id=file_upload_id)
    return content


@router.get("", response_class=HTMLResponse)
async def render_report(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})
