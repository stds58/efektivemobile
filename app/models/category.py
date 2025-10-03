from sqlalchemy.orm import Mapped
from .base import Base, StrUniq


class Category(Base):
    name: Mapped[StrUniq]

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, name={self.name})>"

