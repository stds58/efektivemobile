from pathlib import Path
from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, status, File, UploadFile
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.get_db import auth_db_context
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext
from app.schemas.file_upload import SchemaFileUploadBase, SchemaFileUploadCreate, SchemaFileUploadFilter
from app.services.file_upload import (
    find_many_file_upload,
    add_one_file_upload,
    delete_one_file_upload,
)


logger = structlog.get_logger()

router = APIRouter()


@router.post("", summary="Upload file")
async def upload_file(
    request_context: RequestContext = Depends(
        auth_db_context(
            business_element=BusinessDomain.FILE_UPLOAD,
            isolation_level=IsolationLevel.REPEATABLE_READ,
            commit=True,
        )
    ),
    file: UploadFile = File(...)
) -> SchemaFileUploadBase:
    data = SchemaFileUploadCreate(
        name = Path(file.filename).stem,
        extension = Path(file.filename).suffix.lower(),
        size_bytes = file.size
    )

    logger.info("Upload file", data=data)
    file_upload = await add_one_file_upload(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        data=data,
        session=request_context.session,
        file=file
    )
    logger.info("Uploaded file", data=data)

    return file_upload

