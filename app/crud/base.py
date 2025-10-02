from typing import ClassVar, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel as PydanticModel
from sqlalchemy import and_, select, update
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.models.base import Base
from app.schemas.base import PaginationParams
from app.exceptions.base import MultipleResultsError


assert issubclass(Base, DeclarativeBase)


# pylint: disable-next=no-name-in-module,invalid-name
ModelType = TypeVar("ModelType", bound=Base)
# pylint: disable-next=no-name-in-module,invalid-name
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticModel)
# pylint: disable-next=no-name-in-module,invalid-name
FilterSchemaType = TypeVar("FilterSchemaType", bound=PydanticModel)


# pylint: disable-next=too-few-public-methods
class FiltrMixin:
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


class BaseDAO(FiltrMixin, Generic[ModelType, CreateSchemaType, FilterSchemaType]):
    model: ClassVar[type[ModelType]]
    create_schema: ClassVar[type[CreateSchemaType]]
    filter_schema: ClassVar[type[FilterSchemaType]]
    pydantic_model: ClassVar[type[PydanticModel]]

    @classmethod
    async def find_many(
        cls,
        session: AsyncSession,
        filters: Optional[FilterSchemaType] = None,
        pagination: Optional[PaginationParams] = None,
        order_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[PydanticModel]:
        query = select(cls.model)
        if filters is not None:
            query = cls._apply_filters(query, filters)

        if order_by:
            column = getattr(cls.model, order_by)
            if order.lower() == "desc":
                column = column.desc()
            query = query.order_by(column)

        if pagination:
            query = cls._apply_pagination(query, pagination)
        result = await session.execute(query)
        results = result.unique().scalars().all()
        return [
            cls.pydantic_model.model_validate(obj, from_attributes=True)
            for obj in results
        ]

    @classmethod
    async def find_one(
            cls,
            session: AsyncSession,
            filters: Optional[FilterSchemaType] = None
    ) -> Optional[PydanticModel]:
        query = select(cls.model)
        if filters is not None:
            query = cls._apply_filters(query, filters)

        result = await session.execute(query)
        try:
            obj = result.unique().scalars().one_or_none()
        except MultipleResultsFound as exc:
            raise MultipleResultsError from exc
        if obj is None:
            return None
        return cls.pydantic_model.model_validate(obj, from_attributes=True)

    @classmethod
    async def add_one(cls, session: AsyncSession, values: Dict) -> ModelType:
        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.flush()
        await session.refresh(new_instance)
        return new_instance

    # @classmethod
    # async def add_many(cls, session: AsyncSession, values_list: List[Dict]) -> None:
    #     stmt = insert(cls.model).values(values_list)
    #     stmt = stmt.on_conflict_do_nothing()
    #     await session.execute(stmt)
    #     await session.flush()
    #     await session.commit()

    # @classmethod
    # async def delete_all(cls, session: AsyncSession) -> dict:
    #     query = sqlalchemy_delete(cls.model)
    #     result = await session.execute(query)
    #     return {
    #         "status": "success",
    #         "message": f"{result.rowcount} записей удалено",
    #         "deleted_count": result.rowcount,
    #         "http_status": status.HTTP_200_OK,
    #     }

    # @classmethod
    # async def find_items_since(cls, last_id: int, session: AsyncSession):
    #     result = await session.execute(
    #         select(cls.model).where(cls.model.id > last_id).order_by(cls.model.id)
    #     )
    #     return result.scalars().all()

    @classmethod
    async def update_one(
        cls, model_id: int, values: Dict, session: AsyncSession
    ) -> None:
        stmt = update(cls.model).where(cls.model.id == model_id).values(values)
        await session.execute(stmt)
        await session.commit()
