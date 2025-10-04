from app.crud.base import BaseDAO
from app.models.product import Product
from app.schemas.product import (
    SchemaProductBase,
    SchemaProductCreate,
    SchemaProductFilter,
)


class ProductDAO(BaseDAO[Product, SchemaProductCreate, SchemaProductFilter]):
    model = Product
    create_schema = SchemaProductCreate
    filter_schema = SchemaProductFilter
    pydantic_model = SchemaProductBase

    _exclude_from_filter_by = {"id"}
