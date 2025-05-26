import pytest
from pydantic import ValidationError

from app.schemas.team_schema import TeamCreateSchema


class TestTeamUnitSchema:

    def test_unit_schema_team_validation(self):
        valid_data = {"name": "Team 7"}
        team = TeamCreateSchema(**valid_data)
        assert team.name == valid_data["name"]

        invalid_data = {}
        with pytest.raises(ValidationError):
            TeamCreateSchema(**invalid_data)
