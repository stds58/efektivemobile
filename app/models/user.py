from typing import List
from sqlalchemy import Table, Column, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base, StrUniq, StrNullFalse, StrNullTrue, BoolDefTrue
from app.models.role import Role


class User(Base):
    email: Mapped[StrUniq]
    password: Mapped[StrNullFalse]
    first_name: Mapped[StrNullTrue]
    last_name: Mapped[StrNullTrue]
    is_active: Mapped[BoolDefTrue]

    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="users",
        lazy="selectin",
    )

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="users",
        lazy="selectin",
    )

    file_uploads: Mapped[List["FileUpload"]] = relationship(
        "FileUpload",
        back_populates="users",
        lazy="selectin",
    )

    def __str__(self):
        return f"<{self.__class__.__name__} (id={self.id}, email={self.email!r})>"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, email={self.email})>"
