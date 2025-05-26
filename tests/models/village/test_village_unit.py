import pytest
from pydantic import ValidationError

from app.models import enums
from app.schemas.village_schema import VillageCreateSchema


class TestVillageUnitSchema:

    def test_unit_schema_village_validation(self):
        valid_data = {
            "name": enums.VillageEnum.konoha,
            "country": enums.CountryEnum.fire,
        }
        village = VillageCreateSchema(**valid_data)
        assert village.name == valid_data["name"]

        invalid_data = {"name": enums.VillageEnum.ame}
        with pytest.raises(ValidationError):
            VillageCreateSchema(**invalid_data)
