from typing import List
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from app.models.base import (
    Base,
    StrUniq,
    StrNullFalse,
    StrNullTrue,
    BoolDefTrue,
)
from app.models.role import Role


user_role_association = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)


class User(Base):
    email: Mapped[StrUniq]
    password: Mapped[StrNullFalse]
    first_name: Mapped[StrNullTrue]
    last_name: Mapped[StrNullTrue]
    is_active: Mapped[BoolDefTrue]

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_role_association,
        back_populates="users",
        lazy="selectin",  # Для асинхронной загрузки ролей вместе с пользователем
    )

    def __str__(self):
        return f"<{self.__class__.__name__} (id={self.id}, email={self.email!r})>"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, email={self.email})>"
