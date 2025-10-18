from typing import Optional
from datetime import datetime
from pathlib import Path
import re
from uuid import UUID
from pydantic import BaseModel, field_validator
from app.core.config import settings
from app.exceptions.base import FileSizeError, FileExtensionError, FileNameError


class SchemaFileUploadBase(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    extension: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime


class SchemaFileUploadCreate(BaseModel):
    name: str
    extension: str
    size_bytes: int

    @field_validator("name")
    @classmethod
    def validate_filename(cls, field: str):
        if not field:
            raise FileNameError
        # Очищаем имя от опасных символов
        clean_name = re.sub(r"[^a-zA-Z0-9._\-() ]", "_", field)
        clean_name = clean_name.strip()[:255]
        return clean_name

    @field_validator("extension")
    @classmethod
    def validate_extension(cls, field: str):
        if field not in settings.ALLOW_FILE_EXTENSION:
            raise FileExtensionError
        return field

    @field_validator("size_bytes")
    @classmethod
    def validate_file_size(cls, field: int):
        max_size = settings.FILE_SIZE_LIMIT_MB * 1024 * 1024
        if field > max_size:
            raise FileSizeError
        return field


class SchemaFileUploadFilter(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    extension: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
