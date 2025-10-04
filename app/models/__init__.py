from .base import Base
from .user import User
from .order import Order
from .role import Role
from .access_rule import AccessRule
from .business_element import BusinessElement
from .category import Category
from .product import Product


# Теперь при импорте Base автоматически загружаются все модели
__all__ = [
    "Base",
    "User",
    "Order",
    "Role",
    "AccessRule",
    "BusinessElement",
    "Category",
    "Product",
]
