from typing import TypeVar
from pydantic import BaseModel as PydanticModel
from app.models.base import Base


# pylint: disable-next=no-name-in-module,invalid-name
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=PydanticModel)
SourceModel = TypeVar("SourceModel", bound=Base)
ThroughModel = TypeVar("ThroughModel", bound=Base)
TargetModel = TypeVar("TargetModel", bound=Base)
SourceSchema = TypeVar("SourceSchema", bound=PydanticModel)
