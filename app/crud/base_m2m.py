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
from typing import ClassVar, Generic, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.base import PaginationParams
from app.crud.mixins.types import SourceModel, ThroughModel, TargetModel, SourceSchema, FilterSchemaType
from app.crud.mixins.query_mixin_m2m import QueryMixin


class M2MDAO(QueryMixin, Generic[SourceModel, ThroughModel, TargetModel, SourceSchema, FilterSchemaType]):
    source_model: ClassVar[type[SourceModel]]
    through_model: ClassVar[type[ThroughModel]]
    target_model: ClassVar[type[TargetModel]]
    source_schema: ClassVar[type[SourceSchema]]
    filter_schema: ClassVar[type[FilterSchemaType]]
    target_attr_name: str

    @classmethod
    async def find_many(
        cls,
        session: AsyncSession,
        filters: Optional[FilterSchemaType] = None,
        pagination: Optional[PaginationParams] = None,
        order_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[SourceSchema]:
        query = cls._build_query(filters, pagination, order_by, order)
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
    ) -> SourceSchema:
        query = cls._build_query(filters)
        result = await session.execute(query)
        rows = result.all()
        aggregated_sources = cls._aggregate_m2m_results(rows, cls.target_attr_name)

        return cls.source_schema.model_validate(aggregated_sources[0], from_attributes=True)
