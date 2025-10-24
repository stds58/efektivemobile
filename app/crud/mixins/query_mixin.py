from typing import Optional
from sqlalchemy import and_, Select
from sqlalchemy.orm import DeclarativeBase
from app.schemas.base import PaginationParams
from app.crud.mixins.types import FilterSchemaType


class QueryMixin:
    model: type[DeclarativeBase]
    _exclude_from_filter_by: set[str] = set()

    @classmethod
    def _apply_filters(cls, query, filters: FilterSchemaType):
        """игнорирование полей фильтрации, которых нет в модели"""
        allowed_fields = cls.filter_schema.model_fields.keys()
        exclude_fields = getattr(cls, "_exclude_from_filter_by", set())

        filter_dict = {
            key: value
            for key, value in filters.model_dump().items()
            if key in allowed_fields and key not in exclude_fields and value is not None
        }

        filters_result = []
        for key, value in filter_dict.items():
            if hasattr(cls.model, key):
                filters_result.append(getattr(cls.model, key) == value)
        if filters_result:
            query = query.filter(and_(*filters_result))
        return query

    @classmethod
    def _apply_pagination(cls, query, pagination: PaginationParams):
        return query.limit(pagination.per_page).offset(
            pagination.per_page * (pagination.page - 1)
        )

    @classmethod
    def _build_query(
        cls,
        query: Select,
        filters: Optional[FilterSchemaType] = None,
        pagination: Optional[PaginationParams] = None,
        order_by: Optional[str] = None,
        order: str = "asc",
    ) -> Select:
        if filters is not None:
            query = cls._apply_filters(query, filters)

        if order_by:
            column = getattr(cls.model, order_by)
            if order.lower() == "desc":
                column = column.desc()
            query = query.order_by(column)

        if pagination:
            query = cls._apply_pagination(query, pagination)

        return query
