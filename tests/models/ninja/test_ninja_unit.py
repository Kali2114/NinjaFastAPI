import pytest
from pydantic import ValidationError

from app.models import enums
from app.schemas.ninja_schema import NinjaCreateSchema


class TestNinjaUnitSchema:

    def test_unit_schema_ninja_validation(self):
        user = type("User", (), {"id": 1})()
        valid_data = {
            "name": "Hatake Kakashi",
            "clan": "Hatake",
            "user_id": user.id,
        }
        ninja = NinjaCreateSchema(**valid_data)
        assert ninja.name == valid_data["name"]
        assert ninja.rank == enums.RankEnum.academy

        invalid_data = {
            "name": "Uchiha Sasuke",
            "user_id": user.id,
        }
        with pytest.raises(ValidationError):
            NinjaCreateSchema(**invalid_data)
