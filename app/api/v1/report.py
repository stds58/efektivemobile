from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import structlog
from fastapi import APIRouter, Depends, status


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

@router.get("", response_class=HTMLResponse)
async def report(request: Request):
    # Сортируем по убыванию суммы (опционально)
    sorted_data = sorted(AGGREGATED_DATA.items(), key=lambda x: x[1], reverse=True)
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "data": sorted_data}
    )



