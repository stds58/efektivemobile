from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator


class SchemaUserBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    is_active: bool


class SchemaUserFilter(BaseModel):
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class SchemaUserCreate(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )
    password_confirm: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )
    first_name: str = Field(
        ..., min_length=5, max_length=50, description="Имя, от 5 до 50 знаков"
    )
    last_name: str = Field(
        ..., min_length=5, max_length=50, description="Фамилия, от 5 до 50 знаков"
    )

    @field_validator("password_confirm")
    def passwords_match(cls, v, values):
        if "password" in values.data and v != values.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class SchemaUserPatch(BaseModel):
    password: Annotated[str, StringConstraints(min_length=5, max_length=50)] | None = (
        Field(None)
    )
    first_name: (
        Annotated[str, StringConstraints(min_length=3, max_length=50)] | None
    ) = Field(None)
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=50)] | None = (
        Field(None)
    )


class SchemaUserLogin(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )


class UserPublic(BaseModel):
    created_at: datetime
    updated_at: datetime
    email: EmailStr
    first_name: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    last_name: Annotated[str, StringConstraints(min_length=3, max_length=50)]
    is_active: bool
    role: list[str] | None = None


class UserInDB(BaseModel):
    password: str
