import os
import shutil
from uuid import UUID
import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.core.config import settings
from app.crud.file_upload import FileUploadDAO
from app.schemas.base import PaginationParams
from app.schemas.file_upload import (
    SchemaFileUploadCreate,
    SchemaFileUploadFilter,
    SchemaFileUploadBase,
)
from app.schemas.permission import AccessContext
from app.services.base import (
    find_many_business_element,
    add_one_business_element,
    delete_one_business_element,
)
from app.services.base_scoped_operations import (
    find_one_scoped_by_id,
    find_many_scoped,
    add_one_scoped,
    update_one_scoped,
    delete_one_scoped,
)
from app.exceptions.base import FileStorageError
from openpyxl import load_workbook
from app.utils.file_loader import ExcelLoader, JsonLoader
from app.exceptions.base import FileExtensionError
from app.utils.creator_report_rso import DebtReport


logger = structlog.get_logger()


async def get_report(
    #business_element: BusinessDomain,
    #access: AccessContext,
    #session: AsyncSession,
    file_upload_id=UUID,
    extension=str,
    sheet_name=str,
):
    filename = f"{file_upload_id}{extension}"
    report = DebtReport(
        input_file=filename,
        sheet_name=sheet_name,
    )
    data = report.generate()
    return data
