from typing import List
from sqlalchemy.orm import Mapped, relationship
from .base import Base, StrUniq, StrNullFalse


class Role(Base):
    name: Mapped[StrUniq]
    description: Mapped[StrNullFalse]

    users: Mapped[List["User"]] = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )

    access_rules: Mapped[List["AccessRule"]] = relationship(
        "AccessRule",
        back_populates="role",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, email={self.name})>"
