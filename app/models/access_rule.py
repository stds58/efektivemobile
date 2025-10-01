from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from .base import Base, BoolDefFalse


class AccessRule(Base):
    role_id: Mapped[str] = mapped_column(ForeignKey("role.id"), primary_key=True)
    businesselement_id: Mapped[str] = mapped_column(ForeignKey("businesselement.id"), primary_key=True)

    read_permission: Mapped[BoolDefFalse]
    read_all_permission: Mapped[BoolDefFalse]
    create_permission: Mapped[BoolDefFalse]
    update_permission: Mapped[BoolDefFalse]
    update_all_permission: Mapped[BoolDefFalse]
    delete_permission: Mapped[BoolDefFalse]
    delete_all_permission: Mapped[BoolDefFalse]

    role: Mapped["Role"] = relationship("Role", back_populates="access_rules")
    element: Mapped["BusinessElement"] = relationship("BusinessElement")

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.role_id}, element={self.businesselement_id})>"
