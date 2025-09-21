from sqlalchemy.orm import Mapped
from app.db.base import Base, StrUniq, Str, IsTrue, IsFalse


class User(Base):
    email: Mapped[StrUniq]
    password: Mapped[Str]
    first_name: Mapped[Str]
    last_name: Mapped[Str]
    is_active: Mapped[IsTrue]
    is_user: Mapped[IsTrue]
    is_manager: Mapped[IsFalse]
    is_admin: Mapped[IsFalse]

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.email!r})"

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
