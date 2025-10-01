import pytest
from pydantic import ValidationError

from app.schemas.ninja_schema import NinjaCreateSchema
from app.routers.utils import get_current_user
from app.main import app
from app.models import enums


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
class TestPublicNinjaEndpoints:

    def test_get_ninja_unauthorized(self, client):
        res = client.get("/ninja")
        assert res.status_code == 200

    def test_get_my_ninjas_requires_auth(self, client):
        res = client.get("/ninja/my_ninjas")
        assert res.status_code == 403

    # def test_create_ninja_unauthorized(self, client):
    #     ninja = get_random_ninja_dict()
    #     res = client.post("/ninja", json=ninja)
    #     assert res.status_code == 401
    #
    # def test_delete_ninja_unauthorized(self, client):
    #     res = client.delete("/ninja/1")
    #     assert res.status_code == 401


@pytest.mark.endpoints
class TestPrivateNinjaEndpoints:

    def test_get_my_ninjas_ok(self, client, monkeypatch):
        fake_user = type("User", (), {"id": 42, "username": "tester"})()
        app.dependency_overrides[get_current_user] = lambda: fake_user

        expected = [
            {
                "id": 5,
                "name": "Shikamaru",
                "clan": "Nara",
                "summon_animal": None,
                "village_id": 1,
                "village": None,
                "rank": enums.RankEnum.academy.value,
                "alive": True,
                "forbidden": False,
            },
            {
                "id": 6,
                "name": "Choji",
                "clan": "Akimichi",
                "summon_animal": None,
                "village_id": 1,
                "village": None,
                "rank": enums.RankEnum.academy.value,
                "alive": True,
                "forbidden": False,
            },
        ]

        class FakeQuery:
            def filter(self, *args, **kwargs):
                return self

            def all(self):
                return expected

        shared = FakeQuery()
        monkeypatch.setattr("sqlalchemy.orm.Session.query", lambda self, model: shared)
        res = client.get("/ninja/my_ninjas")
        app.dependency_overrides.clear()

        assert res.status_code == 200
        assert res.json() == expected

    def test_get_my_ninja_detail_other_user_returns_404(self, client, monkeypatch):
        fake_user = type("User", (), {"id": 42})()
        app.dependency_overrides[get_current_user] = lambda: fake_user

        class FakeQuery:
            def filter(self, *args, **kwargs):
                return self

            def first(self):
                return None

        shared = FakeQuery()
        monkeypatch.setattr(
            "sqlalchemy.orm.Session.query",
            lambda _self, _model: shared,
        )

        res = client.get("/ninja/my_ninjas/7")
        app.dependency_overrides.clear()

        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"

    # def test_create_ninja_successful(self, client, monkeypatch):
    #     ninja = get_random_ninja_dict()
    #
    #     monkeypatch.setattr("sqlalchemy.orm.Query.first", mock_output())
    #     monkeypatch.setattr("sqlalchemy.orm.Session.commit", mock_output())
    #     monkeypatch.setattr("sqlalchemy.orm.Session.refresh", mock_output())
    #
    #     body = ninja.copy()
    #     body.pop("id")
    #     res = client.post("/ninja", json=body)
    #     data = res.json()
    #
    #     assert res.status_code == 201
    #     assert data["name"] == body["name"]
    #     assert data["clan"] == body["clan"]
    #     assert "id" in data
    #     assert "user_id" in data
