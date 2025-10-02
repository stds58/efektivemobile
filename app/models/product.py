from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, StrUniq


class Product(Base):
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), primary_key=True)
    name: Mapped[StrUniq]
    price: Mapped[int] = mapped_column(info={"verbose_name": "цена в копейках"})

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name})>"
