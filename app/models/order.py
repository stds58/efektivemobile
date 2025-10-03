from uuid import UUID
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, BoolDefFalse


class Order(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_paid: Mapped[BoolDefFalse]

    users: Mapped["User"] = relationship("User", back_populates="orders")
    products: Mapped["Product"] = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, user_id={self.user_id}, product_id={self.product_id})>"

