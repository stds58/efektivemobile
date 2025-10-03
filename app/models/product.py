from uuid import UUID
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, StrUniq


class Product(Base):
    category_id: Mapped[UUID] = mapped_column(ForeignKey("category.id"))
    name: Mapped[StrUniq]
    price: Mapped[int] = mapped_column(info={"verbose_name": "цена в копейках"})

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="products",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name})>"
