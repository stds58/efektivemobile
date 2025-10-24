from typing import Optional, List, Any, Tuple
from sqlalchemy import select, inspect, and_
from sqlalchemy.orm import foreign
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import DeclarativeBase
from app.schemas.base import PaginationParams
from app.crud.mixins.types import SourceModel, TargetModel, FilterSchemaType


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
            if hasattr(cls.source_model, key):
                filters_result.append(getattr(cls.source_model, key) == value)
        if filters_result:
            query = query.filter(and_(*filters_result))
        return query

    @classmethod
    def _apply_pagination(cls, query, pagination: PaginationParams):
        return query.limit(pagination.per_page).offset(
            pagination.per_page * (pagination.page - 1)
        )

    @staticmethod
    def _aggregate_m2m_results(
        rows: List[Tuple[Any, Any]],
        target_attr_name: str,
    ) -> List[Any]:
        seen_sources = {}
        for source_obj, target_obj in rows:
            if source_obj.id not in seen_sources:
                seen_sources[source_obj.id] = source_obj
                setattr(source_obj, target_attr_name, [])
            if target_obj is not None:
                getattr(source_obj, target_attr_name).append(target_obj)
        return list(seen_sources.values())

    @classmethod
    def _build_query(
        cls,
        filters: Optional[FilterSchemaType] = None,
        pagination: Optional[PaginationParams] = None,
        order_by: Optional[str] = None,
        order: str = "asc",
    ) -> Select[Tuple[SourceModel, TargetModel]]:
        """
        Строит JOIN-запрос для M2M и возвращает query, а также найденные FK (если нужно).
        """
        try:
            inspector = inspect(cls.through_model)
        except Exception as e:
            raise ValueError(
                f"Не удалось проинспектировать through_model: {cls.through_model}. "
                "Убедитесь, что это корректная SQLAlchemy-модель."
            ) from e

        source_fk = None
        target_fk = None

        for column in inspector.columns:
            if column.foreign_keys:
                fk = list(column.foreign_keys)[0]
                referred_table = fk.column.table
                if referred_table.name == cls.source_model.__tablename__:
                    source_fk = column
                elif referred_table.name == cls.target_model.__tablename__:
                    target_fk = column
        if source_fk is None or target_fk is None:
            raise ValueError(
                f"Не найдены foreign keys в {cls.through_model.__name__} к {cls.source_model.__name__} и {cls.target_model.__name__}"
            )

        query = (
            select(cls.source_model, cls.target_model)
            .select_from(cls.source_model)
            .outerjoin(cls.through_model, source_fk == foreign(cls.source_model.id))
            .outerjoin(cls.target_model, target_fk == foreign(cls.target_model.id))
        )

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
