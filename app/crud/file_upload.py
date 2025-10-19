from app.crud.base import BaseDAO
from app.models.file_upload import FileUpload
from app.schemas.file_upload import (
    SchemaFileUploadBase,
    SchemaFileUploadCreate,
    SchemaFileUploadFilter,
)


class FileUploadDAO(
    BaseDAO[FileUpload, SchemaFileUploadCreate, SchemaFileUploadFilter]
):
    model = FileUpload
    create_schema = SchemaFileUploadCreate
    filter_schema = SchemaFileUploadFilter
    pydantic_model = SchemaFileUploadBase
