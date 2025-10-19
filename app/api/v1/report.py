from uuid import UUID
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import structlog
from fastapi import APIRouter, Depends, status
from app.services.report import get_report


logger = structlog.get_logger()

V2_DIR = Path(__file__).resolve().parent
API_DIR = V2_DIR.parent
APP_DIR = API_DIR.parent
TEMPLATES_DIR = APP_DIR / "templates"

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Пример данных (в реальном проекте — из БД или расчёта)
AGGREGATED_DATA = {
    'ВК': 1104902.73,
    'МРГ': 29030.0,
    'ПСК': 3512341.28,
    'ПТЭ': 131776.22,
    'ТГК': 95339.26,
    'ТЭ': 355413.9,
    'ТЭК': 159457.72
}

@router.get("/{file_upload_id}/generate-report")
async def report(
    file_upload_id: UUID,
    extension: str,
    sheet_name: str
):
    logger.info("Get content", model_id=file_upload_id)
    content = await get_report(
        #access=request_context.access,
        #session=request_context.session,
        file_upload_id=file_upload_id,
        extension=extension,
        sheet_name=sheet_name
    )
    logger.info("Geted content", model_id=file_upload_id)
    return content

"""
@router.get("/{file_upload_id}/content", summary="Get content")
async def get_content(
    file_upload_id: UUID,
    sheet_name: str = None,
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.FILE_UPLOAD,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=True,
        )
    ),
):
    logger.info("Get content", model_id=file_upload_id)
    content = await read_content_file(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        session=request_context.session,
        file_upload_id=file_upload_id,
        sheet_name=sheet_name
    )
    logger.info("Geted content", model_id=file_upload_id)
    return content
"""

@router.get("", response_class=HTMLResponse)
async def report(request: Request):
    # Сортируем по убыванию суммы (опционально)
    sorted_data = sorted(AGGREGATED_DATA.items(), key=lambda x: x[1], reverse=True)
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "data": sorted_data}
    )
