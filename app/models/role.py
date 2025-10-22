from typing import List
from sqlalchemy.orm import Mapped, relationship
from .base import Base, StrUniq, StrNullFalse


class Role(Base):
    name: Mapped[StrUniq]
    description: Mapped[StrNullFalse]

    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="roles",
        lazy="selectin"
    )

    access_rules: Mapped[List["AccessRule"]] = relationship(
        "AccessRule",
        back_populates="role",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name})>"
