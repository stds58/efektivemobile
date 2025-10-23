from app.crud.base import BaseDAO
from app.models.business_element import BusinessElement
from app.schemas.business_element import SchemaBusinessElementBase, SchemaBusinessElementFilter


class BusinessElementDAO(BaseDAO[BusinessElement, None, SchemaBusinessElementFilter]):
    model = BusinessElement
    create_schema = None
    filter_schema = SchemaBusinessElementFilter
    pydantic_model = SchemaBusinessElementBase
