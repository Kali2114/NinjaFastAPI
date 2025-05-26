from pydantic import BaseModel

from typing import Optional

from app.models import enums


class VillageBaseSchema(BaseModel):
    name: enums.VillageEnum
    country: enums.CountryEnum


class VillageReadSchema(VillageBaseSchema):
    id: int
    kage: Optional[int] = None
    kage_id: Optional[int] = None


class VillageCreateSchema(VillageBaseSchema):
    pass
