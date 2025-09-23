from sqlalchemy import String, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDPk, CreatedAt, UpdatedAt, StrUniq, StrNullFalse, StrNullTrue
from typing import List
from .permission import role_permission_association


class Role(Base):
    name: Mapped[StrUniq]
    description: Mapped[StrNullFalse]

    # Связь с пользователями
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )
    # Связь с разрешениями
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permission_association,
        back_populates="roles",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, email={self.name})>"
