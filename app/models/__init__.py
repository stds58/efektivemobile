from .base import Base
from .user import User
from .order import Order
from .role import Role
from .user_role import UserRole
from .access_rule import AccessRule
from .business_element import BusinessElement
from .category import Category
from .product import Product
from .file_upload import FileUpload


# Теперь при импорте Base автоматически загружаются все модели
__all__ = [
    "Base",
    "User",
    "Order",
    "Role",
    "UserRole",
    "AccessRule",
    "BusinessElement",
    "Category",
    "Product",
    "FileUpload",
]
