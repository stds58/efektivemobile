from datetime import datetime
from typing import Annotated
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
    is_user: bool
    is_manager: bool
    is_admin: bool


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
    is_active: bool | None = Field(None)
    is_user: bool | None = Field(None)
    is_manager: bool | None = Field(None)
    is_admin: bool | None = Field(None)


class SchemaUserLogin(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(
        ..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )


class UserPublic(BaseModel):
    id: UUID
    is_active: bool


class UserInDB(BaseModel):
    password: str
