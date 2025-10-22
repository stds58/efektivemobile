"""
SELECT T1.*, T3.*
FROM <source_model> as T1
LEFT OUTER JOIN <through_model> as T2 ON T1.id = T2.FK
LEFT OUTER JOIN <target_model> as T3 ON T3.id = T2.FK

stmt = (
    select(User.email, Role.name)
    .select_from(User)
    .outerjoin(UserRole, User.id == UserRole.user_id)
    .outerjoin(Role, UserRole.role_id == Role.id)
)
"""
from typing import ClassVar, Type, TypeVar, Generic, Optional, List, Any, Tuple
from uuid import UUID
from sqlalchemy import select, inspect, and_
from sqlalchemy.orm import DeclarativeBase, selectinload, foreign, remote
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as PydanticModel
from app.models.base import Base
from app.schemas.base import PaginationParams


# pylint: disable-next=no-name-in-module,invalid-name
SourceModel = TypeVar("SourceModel", bound=Base)
ThroughModel = TypeVar("ThroughModel", bound=Base)
TargetModel = TypeVar("TargetModel", bound=Base)
SourceSchema = TypeVar("SourceSchema", bound=PydanticModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=PydanticModel)


class M2MDAO(Generic[SourceModel, ThroughModel, TargetModel, SourceSchema, FilterSchemaType]):
    source_model: ClassVar[type[SourceModel]]
    through_model: ClassVar[type[ThroughModel]]
    target_model: ClassVar[type[TargetModel]]
    source_schema: ClassVar[type[SourceSchema]]
    filter_schema: ClassVar[type[FilterSchemaType]]
    target_attr_name: str

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
    def _build_m2m_query(cls) -> Select[Tuple[SourceModel, TargetModel]]: # либо Select[Any]
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
                f"Не найдены foreign keys в {cls.through_model.__name__} к {cls.source_model.__name__} и {cls.target_model.__name__}")

        query = (
            select(cls.source_model, cls.target_model)
            .select_from(cls.source_model)
            .outerjoin(cls.through_model, source_fk == foreign(cls.source_model.id))
            .outerjoin(cls.target_model, target_fk == foreign(cls.target_model.id))
        )

        return query

    @classmethod
    async def find_many(
        cls,
        session: AsyncSession,
        filters: Optional[FilterSchemaType] = None,
        pagination: Optional[PaginationParams] = None,
        order_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[SourceSchema]:
        query = cls._build_m2m_query()
        result = await session.execute(query)
        rows = result.all()
        aggregated_sources = cls._aggregate_m2m_results(rows, cls.target_attr_name)

        return [
            cls.source_schema.model_validate(obj, from_attributes=True)
            for obj in aggregated_sources
        ]

    @classmethod
    async def find_one(
            cls,
            session: AsyncSession,
            filters: Optional[FilterSchemaType] = None
    ) -> List[SourceSchema]:
        query = cls._build_m2m_query()
        if filters is not None:
            query = cls._apply_filters(query, filters)
        result = await session.execute(query)
        rows = result.all()
        aggregated_sources = cls._aggregate_m2m_results(rows, cls.target_attr_name)

        return [
            cls.source_schema.model_validate(obj, from_attributes=True)
            for obj in aggregated_sources
        ]
