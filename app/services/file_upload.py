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
)
from app.schemas.permission import AccessContext
from app.services.base_scoped_operations import (
    find_one_scoped_by_id,
    find_many_scoped,
    add_one_scoped,
    delete_one_scoped,
)
from app.exceptions.base import FileStorageError
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
    return await find_many_scoped(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        filters=filters,
        session=session,
        pagination=pagination,
        owner_field="user_id",
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
        raise FileStorageError(
            custom_detail=f"Ошибка сохранения файла: {str(e)}"
        ) from e
    return file_upload


async def delete_one_file_upload(
    business_element: BusinessDomain,
    access: AccessContext,
    session: AsyncSession,
    file_upload_id: UUID,
):
    file_upload = await delete_one_scoped(
        business_element=business_element,
        methodDAO=FileUploadDAO,
        access=access,
        session=session,
        business_element_id=file_upload_id,
    )

    file_upload_id = str(file_upload.id)
    file_path = os.path.join(
        settings.USER_UPLOADS_DIR, f"{file_upload_id}{file_upload.extension}"
    )

    if os.path.exists(file_path):
        os.remove(file_path)
        print("Файл удалён")
    else:
        print("Файл не существует")

    return file_upload


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
