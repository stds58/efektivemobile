from pathlib import Path
from uuid import UUID
import structlog
from fastapi import APIRouter, Depends, File, UploadFile, status
from app.core.enums import BusinessDomain, IsolationLevel
from app.dependencies.private_router import private_route_dependency
from app.schemas.base import PaginationParams
from app.schemas.permission import RequestContext
from app.schemas.file_upload import (
    SchemaFileUploadBase,
    SchemaFileUploadCreate,
    SchemaFileUploadFilter,
)
from app.services.file_upload import (
    find_one_file_upload_by_id,
    find_many_file_upload,
    add_one_file_upload,
    read_content_file,
    delete_one_file_upload,
)


logger = structlog.get_logger()

router = APIRouter()

OWNER_FIELD = "user_id"


@router.get("", summary="Upload file")
async def get_upload_files(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.FILE_UPLOAD,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    filters: SchemaFileUploadFilter = Depends(),
    pagination: PaginationParams = Depends(),
):
    logger.info(
        "Get upload_files",
        owner_field=OWNER_FIELD,
        filters=filters,
        pagination=pagination,
    )
    file_upload = await find_many_file_upload(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        filters=filters,
        session=request_context.session,
        pagination=pagination,
    )
    logger.info(
        "Geted upload_files",
        owner_field=OWNER_FIELD,
        filters=filters,
        pagination=pagination,
    )
    return file_upload


@router.get("/{file_upload_id}", summary="Get sheets in excell file")
async def get_sheets(
    file_upload_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.FILE_UPLOAD,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Get sheet", model_id=file_upload_id)
    file_upload = await find_one_file_upload_by_id(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        session=request_context.session,
        file_upload_id=file_upload_id,
    )
    logger.info("Geted sheet", model_id=file_upload_id)
    return file_upload


@router.get("/{file_upload_id}/content", summary="Get content")
async def get_content(
    file_upload_id: UUID,
    sheet_name: str = None,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.FILE_UPLOAD,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Get content", model_id=file_upload_id)
    content = await read_content_file(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        session=request_context.session,
        file_upload_id=file_upload_id,
        sheet_name=sheet_name,
    )
    logger.info("Geted content", model_id=file_upload_id)
    return content


@router.post("", summary="Upload file")
async def upload_file(
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.FILE_UPLOAD,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
    file: UploadFile = File(...),
) -> SchemaFileUploadBase:
    data = SchemaFileUploadCreate(
        name=Path(file.filename).stem,
        extension=Path(file.filename).suffix.lower(),
        size_bytes=file.size,
    )

    logger.info("Upload file", data=data)
    file_upload = await add_one_file_upload(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        data=data,
        session=request_context.session,
        file=file,
    )
    logger.info("Uploaded file", data=data)

    return file_upload


@router.delete(
    "/{file_upload_id}", summary="Delete file", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    file_upload_id: UUID,
    request_context: RequestContext = private_route_dependency(
        business_element=BusinessDomain.FILE_UPLOAD,
        isolation_level=IsolationLevel.REPEATABLE_READ,
    ),
):
    logger.info("Delete file", model_id=file_upload_id)
    await delete_one_file_upload(
        business_element=BusinessDomain.FILE_UPLOAD,
        access=request_context.access,
        session=request_context.session,
        file_upload_id=file_upload_id,
    )
    logger.info("Deleted file", model_id=file_upload_id)
    return
