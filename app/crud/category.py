from app.crud.base import BaseDAO
from app.models.category import Category
from app.schemas.category import SchemaCategoryBase, SchemaCategoryCreate, SchemaCategoryFilter


class CategoryDAO(BaseDAO[Category, SchemaCategoryCreate, SchemaCategoryFilter]):
    model = Category
    create_schema = SchemaCategoryCreate
    filter_schema = SchemaCategoryFilter
    pydantic_model = SchemaCategoryBase
