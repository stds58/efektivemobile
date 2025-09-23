"""
DeclarativeBase:
    Основной класс для всех моделей, от которого будут наследоваться все таблицы (модели таблиц).
    Эту особенность класса мы будем использовать неоднократно.
AsyncAttrs:
    Позволяет создавать асинхронные модели, что улучшает
    производительность при работе с асинхронными операциями.
create_async_engine:
    Функция, создающая асинхронный движок для соединения с базой данных по предоставленному URL.
async_sessionmaker:
    Фабрика сессий для асинхронного взаимодействия с базой данных.
    Сессии используются для выполнения запросов и транзакций.
"""
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func, UUID as SQLAlchemyUUID, text, true, false
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, declared_attr, Mapped


# настройка аннотаций
IntPk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
UUIDPk = Annotated[
    UUID,
    mapped_column(
        SQLAlchemyUUID(as_uuid=True),  # храним как UUID в БД, не как строку
        primary_key=True,
        default=uuid4,  # генерируется на стороне Python
        server_default=None
    )
]
StrUniq = Annotated[str, mapped_column(unique=True, nullable=False)]
StrNullFalse = Annotated[str, mapped_column(nullable=False)]
StrNullTrue = Annotated[str, mapped_column(nullable=True)]
CreatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
]
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    ),
]
BoolDefTrue = Annotated[
    bool,
    mapped_column(
        default=True,
        server_default=true(),
        nullable=False
    )
]
BoolDefFalse = Annotated[
    bool,
    mapped_column(
        default=False,
        server_default=false(),
        nullable=False
    )
]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUIDPk]
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    @declared_attr.directive
    # pylint: disable-next=no-self-argument
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
