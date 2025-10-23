from typing import ClassVar, Dict, Generic, List, Optional
from uuid import UUID
import structlog
from pydantic import BaseModel as PydanticModel
from sqlalchemy import select, update, delete
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.base import PaginationParams
from app.exceptions.base import MultipleResultsError, ObjectsNotFoundByIDError
from app.crud.mixins.query_mixin import QueryMixin
from app.crud.mixins.types import ModelType, CreateSchemaType, FilterSchemaType


logger = structlog.get_logger()


class BaseDAO(QueryMixin, Generic[ModelType, CreateSchemaType, FilterSchemaType]):
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
        query = cls._build_query(query, filters, pagination, order_by, order)
        result = await session.execute(query)
        results = result.unique().scalars().all()
        return [
            cls.pydantic_model.model_validate(obj, from_attributes=True)
            for obj in results
        ]

    @classmethod
    async def find_one(
        cls, session: AsyncSession, filters: Optional[FilterSchemaType] = None
    ) -> Optional[PydanticModel]:
        query = select(cls.model)
        query = cls._build_query(query, filters)
        result = await session.execute(query)
        try:
            obj = result.unique().scalars().one_or_none()
        except MultipleResultsFound as exc:
            logger.error("MultipleResultsError", filters=filters, error=exc)
            raise MultipleResultsError from exc
        if obj is None:
            return None
        return cls.pydantic_model.model_validate(obj, from_attributes=True)

    @classmethod
    async def find_one_by_id(
        cls, session: AsyncSession, model_id: UUID
    ) -> Optional[PydanticModel]:
        obj = await session.get(cls.model, model_id)

        if obj is None:
            logger.error(
                "ObjectsNotFoundByIDError on find_one_by_id",
                model_id=model_id,
                error="Запрашиваемый объект не найден",
            )
            raise ObjectsNotFoundByIDError

        return cls.pydantic_model.model_validate(obj, from_attributes=True)

    @classmethod
    async def add_one(cls, session: AsyncSession, values: Dict) -> ModelType:
        """добавляет 1 запись"""
        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.flush()
        await session.refresh(new_instance)
        return new_instance

    @classmethod
    async def delete_one_by_id(
        cls, session: AsyncSession, model_id: UUID
    ) -> Optional[ModelType]:
        """Удаляет запись по id. Возвращает удалённый объект"""
        obj = await session.get(cls.model, model_id)

        if obj is None:
            logger.error(
                "ObjectsNotFoundByIDError on delete",
                model_id=model_id,
                error="Запрашиваемый объект не найден",
            )
            raise ObjectsNotFoundByIDError

        await session.delete(obj)
        # await session.commit()
        return obj

    @classmethod
    async def delete_many_by_ids(cls, session: AsyncSession, ids: List[UUID]) -> dict:
        """Удаляет записи по списку ID. Возвращает количество удалённых строк"""
        if not ids:
            logger.error("Запрашиваемые объекты не найдены", model_id=List[UUID])
            raise ObjectsNotFoundByIDError

        stmt = delete(cls.model).where(cls.model.id.in_(ids))
        result = await session.execute(stmt)
        return result.rowcount

    @classmethod
    async def update_one(cls, model_id: UUID, values: Dict, session: AsyncSession):
        stmt = (
            update(cls.model)
            .where(cls.model.id == model_id)
            .values(**values)
            .returning(cls.model)
        )
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()

        if obj is None:
            logger.error(
                "ObjectsNotFoundByIDError on update",
                model_id=model_id,
                error="Запрашиваемый объект не найден",
            )
            raise ObjectsNotFoundByIDError

        return obj
