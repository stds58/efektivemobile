from typing import List
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from .base import Base, StrNullFalse, StrNullTrue


# Связующая таблица для связи "многие-ко-многим" между ролями и разрешениями
role_permission_association = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', ForeignKey('role.id'), primary_key=True),
    Column('permission_id', ForeignKey('permission.id'), primary_key=True)
)

class Permission(Base):
    resource: Mapped[StrNullFalse]
    action: Mapped[StrNullFalse]
    description: Mapped[StrNullTrue]

    # Связь с ролями
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permission_association,
        back_populates="permissions"
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, {self.resource}, email={self.action})>"
