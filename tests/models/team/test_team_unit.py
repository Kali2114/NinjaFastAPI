import pytest
from pydantic import ValidationError

from app.schemas.team_schema import TeamCreateSchema


@pytest.mark.unit_schema
class TestTeamUnitSchema:

    def test_unit_schema_team_validation(self):
        valid_data = {"name": "Team 7", "sensei_id": 4}
        team = TeamCreateSchema(**valid_data)
        assert team.name == valid_data["name"]

        invalid_data = {}
        with pytest.raises(ValidationError):
            TeamCreateSchema(**invalid_data)
