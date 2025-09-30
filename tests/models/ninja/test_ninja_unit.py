import pytest
from pydantic import ValidationError

from app.models import enums
from app.schemas.ninja_schema import NinjaCreateSchema
from tests.factories.models_factory import get_random_ninja_dict


def mock_output(return_value=None):
    return lambda *args, **kwargs: return_value


@pytest.mark.unit_schema
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


@pytest.mark.endpoints
class TestPrivateNinjaEndpoints:

    def test_get_ninja_unauthorized(self, client):
        res = client.get("/ninja")
        assert res.status_code == 200

    def test_get_my_ninjas_requires_auth(self, client):
        res = client.get("/ninja/my_ninjas")
        assert res.status_code == 403

    def test_create_ninja_unauthorized(self, client):
        ninja = get_random_ninja_dict()
        res = client.post("/ninja", json=ninja)
        assert res.status_code == 401

    def test_delete_ninja_unauthorized(self, client):
        res = client.delete("/ninja/1")
        assert res.status_code == 401


@pytest.mark.endpoints
class TestPublicNinjaEndpoints:

    # def test_get_my_ninja(self, client, monkeypatch):
    #     user = create_test_user()
    #     ninja1 = get_random_ninja_dict()

    def test_create_ninja_successful(self, client, monkeypatch):
        ninja = get_random_ninja_dict()

        monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
        monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
        monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())

        body = ninja.copy()
        body.pop("id")
        res = client.post("/ninja", json=body)
        data = res.json()

        assert res.status_code == 201
        assert data["name"] == body["name"]
        assert data["clan"] == body["clan"]
        assert "id" in data
        assert "user_id" in data

    def test_delete_ninja_successful(self, client, monkeypatch):
        pass
