from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base,StrNullFalse


class FileUpload(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    name: Mapped[StrNullFalse]
    extension: Mapped[StrNullFalse]
    size_bytes: Mapped[int] = mapped_column(default=0)

    users: Mapped["User"] = relationship("User", back_populates="file_uploads")

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id}, user_id={self.user_id}, name={self.name})>"

