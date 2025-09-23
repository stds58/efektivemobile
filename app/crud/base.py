from typing import AsyncGenerator, ClassVar, Dict, Generic, List, Optional, TypeVar, Type, Any
from fastapi import status
from pydantic import BaseModel as PydanticModel
from sqlalchemy import and_, select, update
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.models.base import Base
from app.schemas.base import PaginationParams


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
            k: v
            for k, v in filters.model_dump().items()
            if k in allowed_fields and k not in exclude_fields and v is not None
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
        return query.limit(pagination.per_page).offset(pagination.per_page * (pagination.page - 1))


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
            if hasattr(filters, "form_id_prefix") and filters.form_id_prefix is not None:
                if hasattr(cls.model, "form_id"):
                    query = query.where(cls.model.form_id.like(f"{filters.form_id_prefix}%"))
                else:
                    raise AttributeError(f"Model {cls.model.__name__} has no attribute 'form_id'")
        if order_by:
            column = getattr(cls.model, order_by)
            if order.lower() == "desc":
                column = column.desc()
            query = query.order_by(column)

        if pagination:
            query = cls._apply_pagination(query, pagination)
        result = await session.execute(query)
        results = result.unique().scalars().all()
        return [cls.pydantic_model.model_validate(obj, from_attributes=True) for obj in results]

    @classmethod
    async def add_one(cls, session: AsyncSession, values: Dict) -> ModelType:
        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.flush()
        await session.refresh(new_instance)
        return new_instance

    @classmethod
    async def add_many(cls, session: AsyncSession, values_list: List[Dict]) -> None:
        stmt = insert(cls.model).values(values_list)
        stmt = stmt.on_conflict_do_nothing()
        await session.execute(stmt)
        await session.flush()
        await session.commit()

    @classmethod
    async def delete_all(cls, session: AsyncSession) -> dict:
        query = sqlalchemy_delete(cls.model)
        result = await session.execute(query)
        return {
            "status": "success",
            "message": f"{result.rowcount} записей удалено",
            "deleted_count": result.rowcount,
            "http_status": status.HTTP_200_OK,
        }

    @classmethod
    async def find_items_since(cls, last_id: int, session: AsyncSession):
        result = await session.execute(select(cls.model).where(cls.model.id > last_id).order_by(cls.model.id))
        return result.scalars().all()

    @classmethod
    async def update_one(cls, model_id: int, values: Dict, session: AsyncSession) -> None:
        stmt = update(cls.model).where(cls.model.id == model_id).values(values)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: FilterSchemaType = None) -> Optional[ModelType]:
        query = select(cls.model)
        if filters is not None:
            if isinstance(filters, dict):
                filter_dict = filters  # Если filters уже словарь, используем его напрямую
            else:
                # Если filters — это Pydantic-модель, преобразуем её в словарь
                filter_dict = filters.model_dump(exclude_unset=True)
            # filter_dict = filters.model_dump(exclude_unset=True)
            filter_dict = {key: value for key, value in filter_dict.items() if value is not None}
            query = query.filter_by(**filter_dict)
        result = await session.execute(query)
        return result.scalar_one_or_none()


ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: ModelType, obj_in) -> ModelType:
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        obj = await self.get(db, id)
        await db.delete(obj)
        await db.commit()
        return obj

