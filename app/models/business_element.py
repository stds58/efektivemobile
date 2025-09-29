from sqlalchemy.orm import Mapped
from .base import Base, StrNullTrue, StrUniq


class BusinessElement(Base):
    name: Mapped[StrUniq]
    description: Mapped[StrNullTrue]

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, {self.name})>"
