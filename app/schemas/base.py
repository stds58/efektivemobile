from pydantic import BaseModel, ConfigDict
from fastapi import Query
from typing import Annotated


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Удалять начальные и конечные пробелы для типов str
        from_attributes=True,  # Разрешить работу с ORM-объектами
        populate_by_name=True,  # Разрешить использование алиасов
        use_enum_values=True,  # Использовать значения ENUM вместо объектов
        #extra="ignore",  # Игнорировать лишние поля
        extra="forbid",
        max_recursion_depth=1,
    )


class BaseFilter(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        #extra="ignore",  # Позволяет игнорировать лишние поля
        extra="forbid",  # Запретить передачу лишних полей
    )


class PaginationParams(BaseModel):
    page: Annotated[int, Query(default=1, ge=1)]
    per_page: Annotated[int, Query(default=10, ge=1, lt=100)]
