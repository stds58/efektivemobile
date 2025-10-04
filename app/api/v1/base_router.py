from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router
from app.api.v1.product import router as product_router
from app.api.v1.category import router as category_router
from app.api.v1.order import router as order_router
from app.api.v1.access_rule import router as access_rule_router


v1_router = APIRouter(prefix="/v1")


v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(user_router, prefix="/users", tags=["user"])
v1_router.include_router(product_router, prefix="/products", tags=["product"])
v1_router.include_router(category_router, prefix="/categorys", tags=["category"])
v1_router.include_router(order_router, prefix="/orders", tags=["order"])
v1_router.include_router(
    access_rule_router, prefix="/access_rules", tags=["access_rule"]
)
