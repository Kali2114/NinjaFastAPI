from pydantic import BaseModel, StringConstraints

from typing import Annotated, Optional

from app.models import enums
from app.schemas.village_schema import VillageReadSchema


class NinjaBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1)]
    clan: Annotated[str, StringConstraints(min_length=1)]
    summon_animal: Optional[str] = None


class NinjaCreateSchema(NinjaBase):
    kekkei_genkai: Optional[enums.KekkeiGenkaiEnum] = enums.KekkeiGenkaiEnum.none
    jinchuriki: Optional[enums.JinchurikiEnum] = enums.JinchurikiEnum.none
    rank: enums.RankEnum = enums.RankEnum.academy


class NinjaPublicReadSchema(NinjaBase):
    id: int
    village_id: int
    village: Optional[VillageReadSchema]
    rank: enums.RankEnum
    alive: bool
    forbidden: bool


class NinjaPrivateReadSchema(NinjaPublicReadSchema):
    level: int
    experience: int
    mission_completed: int
    chakra: int
    team_id: Optional[int] = None
    team: int
    user_id: int
    user: int
    sensei: Optional[str] = None
    kekkei_genkai: enums.KekkeiGenkaiEnum
    chakra_nature: Optional[list[str]] = None
    jinchuriki: enums.JinchurikiEnum
