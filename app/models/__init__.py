from .base import Base
from .user import User
from .role import Role
from .access_rule import AccessRule
from .business_element import BusinessElement


# Теперь при импорте Base автоматически загружаются все модели
__all__ = ["Base", "User", "Role", "AccessRule", "BusinessElement"]
