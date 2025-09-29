from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleInDB(RoleBase):
    id: UUID

    class Config:
        from_attributes = True
