from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class UserRole(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("role.id"), primary_key=True)

    users: Mapped["User"] = relationship("User", back_populates="user_roles")
    roles: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __str__(self):
        return f"<{self.__class__.__name__} (id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"
