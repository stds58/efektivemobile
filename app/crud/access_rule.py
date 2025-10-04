from app.crud.base import BaseDAO
from app.models.access_rule import AccessRule
from app.schemas.access_rule import SchemaAccessRuleBase, SchemaAccessRuleFilter


class AccessRuleDAO(BaseDAO[AccessRule, None, SchemaAccessRuleFilter]):
    model = AccessRule
    create_schema = None
    filter_schema = SchemaAccessRuleFilter
    pydantic_model = SchemaAccessRuleBase

    _exclude_from_filter_by = {"created_at", "updated_at"}
