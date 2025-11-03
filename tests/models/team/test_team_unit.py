import pytest
from pydantic import ValidationError

from app.schemas.team_schema import TeamCreateSchema
from app.main import app
from app.routers.utils import get_current_user, get_db_session


@pytest.mark.unit_schema
class TestTeamUnitSchema:

    def test_unit_schema_team_validation(self):
        valid_data = {"name": "Team 7", "sensei_id": 4}
        team = TeamCreateSchema(**valid_data)
        assert team.name == valid_data["name"]

        invalid_data = {}
        with pytest.raises(ValidationError):
            TeamCreateSchema(**invalid_data)

    def test_create_team_successful(self, client):
        fake_user = type("User", (), {"id": 12})()
        app.dependency_overrides[get_current_user] = lambda: fake_user

        class FakeSession:
            def add(self, obj):
                setattr(obj, "id", 1)

            def flush(self):
                pass

            def commit(self):
                pass

            def refresh(self, obj=None):
                pass

        app.dependency_overrides[get_db_session] = lambda: FakeSession()

        payload = {"name": "Team 7"}
        res = client.post("/team", json=payload)
        assert res.status_code == 201
        assert res.json()["name"] == payload["name"]
        assert res.json()["id"] == 1

        app.dependency_overrides.clear()

    def test_create_team_409_duplicate(self, client):
        fake_user = type("User", (), {"id": 11})()
        app.dependency_overrides[get_current_user] = lambda: fake_user

        class FakeSession:
            def add(self):
                raise ValueError("Duplicate team name.")

            def flush(self):
                pass

            def commit(self):
                pass

            def refresh(self, obj=None):
                pass

        app.dependency_overrides[get_db_session] = FakeSession()

        payload = {"name": "Team 1"}
        res = client.post("/team", json=payload)
        assert res.status_code == 409
        assert res.json()["detail"].lower().startswith("duplicate")

        app.dependency_overrides.clear()
