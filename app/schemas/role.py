from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleInDB(RoleBase):
    id: UUID

    class Config:
        from_attributes = True
