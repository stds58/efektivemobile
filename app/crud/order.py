from app.crud.base import BaseDAO
from app.models.order import Order
from app.schemas.order import SchemaOrderBase, SchemaOrderCreate, SchemaOrderFilter


class OrderDAO(BaseDAO[Order, SchemaOrderCreate, SchemaOrderFilter]):
    model = Order
    create_schema = SchemaOrderCreate
    filter_schema = SchemaOrderFilter
    pydantic_model = SchemaOrderBase
