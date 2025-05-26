from pydantic import BaseModel

from typing import Optional

from app.schemas.ninja_schema import NinjaPublicReadSchema


class TeamBaseSchema(BaseModel):
    name: str


class TeamReadSchema(TeamBaseSchema):
    id: int
    sensei: Optional[NinjaPublicReadSchema] = None
    members: list[NinjaPublicReadSchema] = []


class TeamCreateSchema(TeamBaseSchema):
    pass
