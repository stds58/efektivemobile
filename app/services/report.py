from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import BusinessDomain
from app.crud.file_upload import FileUploadDAO
from app.schemas.permission import AccessContext
from app.services.base_scoped_operations import (
    find_one_scoped_by_id,
)
from app.utils.creator_report_rso import DebtReport


logger = structlog.get_logger()


async def get_report(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    file_upload_id=UUID,
    extension=str,
    sheet_name=str,
):
    file = await find_one_scoped_by_id(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        session=session,
        business_element_id=file_upload_id,
    )

    filename = f"{file_upload_id}{file.extension}"
    report = DebtReport(
        input_file=filename,
        sheet_name=sheet_name,
    )
    data = report.generate()
    return data
