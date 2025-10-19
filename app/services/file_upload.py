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


logger = structlog.get_logger()


async def find_one_file_upload_by_id(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    file_upload_id=UUID,
):
    file = await find_one_scoped_by_id(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        session=session,
        business_element_id=file_upload_id,
    )
    if file.extension in [".xlsx", ".xls"]:
        filename = f"{str(file.id)}{file.extension}"
        loader = ExcelLoader(filename)
        file.sheet = loader.get_sheet_names()
    return file


async def find_many_file_upload(
    business_element: BusinessDomain,
    access: AccessContext,
    filters: SchemaFileUploadFilter,
    session: AsyncSession,
    pagination: PaginationParams,
):
    return await find_many_business_element(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
    )


async def add_one_file_upload(
    business_element: BusinessDomain,
    access: AccessContext,
    data: SchemaFileUploadCreate,
    session: AsyncSession,
    file: UploadFile,
):
    file_upload = await add_one_scoped(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        data=data,
        session=session,
    )
    file_upload_id = str(file_upload.id)
    file_path = os.path.join(
        settings.USER_UPLOADS_DIR, f"{file_upload_id}{data.extension}"
    )
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except OSError as e:
        raise FileStorageError(custom_detail=f"Ошибка сохранения файла: {str(e)}")
    return file_upload


async def delete_one_file_upload(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    file_upload_id: UUID,
):
    return await delete_one_business_element(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        session=session,
        business_element_id=file_upload_id,
    )


async def read_content_file(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    file_upload_id=UUID,
    sheet_name=str,
):
    file = await find_one_scoped_by_id(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        session=session,
        business_element_id=file_upload_id,
    )
    filename = f"{file.id}{file.extension}"
    if file.extension in [".xlsx", ".xls"]:
        if sheet_name is None:
            raise FileExtensionError(
                "Не указан лист екселя, из которого надо получить данные"
            )
        loader = ExcelLoader(filename)
        df = loader.load_data(sheet_name)
        data = loader.clean_dataframe_for_json(df)
    elif file.extension in [".json"]:
        loader = JsonLoader(filename)
        data = loader.load_data()
    else:
        raise FileExtensionError
    return data
