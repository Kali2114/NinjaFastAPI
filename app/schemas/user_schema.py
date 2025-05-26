from pydantic import BaseModel, StringConstraints, EmailStr

from datetime import datetime
from typing import Annotated

from app.schemas.ninja_schema import NinjaPublicReadSchema


class UserBase(BaseModel):
    username: Annotated[str, StringConstraints(min_length=1)]
    email: EmailStr


class UserReadSchema(UserBase):
    id: int
    is_active: bool
    ninjas: list[NinjaPublicReadSchema] = []
    created_at: datetime


class UserCreateSchema(UserBase):
    password: Annotated[str, StringConstraints(min_length=1)]
