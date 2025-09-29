from .base import Base
from .user import User
from .role import Role
from .permission import Permission

# Теперь при импорте Base автоматически загружаются все модели
__all__ = ["Base", "User", "Role", "Permission"]
