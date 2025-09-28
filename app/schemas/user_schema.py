from pydantic import BaseModel, StringConstraints, EmailStr, Field

from datetime import datetime
from typing import Annotated

from app.schemas.ninja_schema import NinjaPublicReadSchema


username = Annotated[str, StringConstraints(min_length=1)]
password = Annotated[str, StringConstraints(min_length=6)]


class UserBase(BaseModel):
    username: username
    email: EmailStr


class UserReadSchema(UserBase):
    id: int
    is_active: bool
    ninjas: list[NinjaPublicReadSchema] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreateSchema(UserBase):
    password: password


class UserLoginSchema(BaseModel):
    username: username
    password: password
