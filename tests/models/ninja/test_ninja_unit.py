import pytest
from pydantic import ValidationError

from app.schemas.ninja_schema import NinjaCreateSchema
from app.routers.utils import get_current_user
from app.db_connection import get_db_session
from app.main import app
from app.models import enums
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
class TestPublicNinjaEndpoints:

    def test_get_ninja_unauthorized(self, client):
        res = client.get("/ninja")
        assert res.status_code == 200

    def test_get_my_ninjas_requires_auth(self, client):
        res = client.get("/ninja/my_ninjas")
        assert res.status_code == 403

    def test_create_ninja_unauthorized(self, client):
        ninja = get_random_ninja_dict()
        res = client.post("/ninja", json=ninja)
        assert res.status_code == 403

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

    def test_create_ninja_successful(self, client, monkeypatch):

        fake_user = type("User", (), {"id": 42, "username": "tester"})
        app.dependency_overrides[get_current_user] = lambda: fake_user

        class FakeSession:
            def add(self, obj):
                obj.id = 123
                obj.user_id = 42
                if getattr(obj, "village_id", None) is None:
                    obj.village_id = 1
                if getattr(obj, "alive", None) is None:
                    obj.alive = True
                if getattr(obj, "forbidden", None) is None:
                    obj.forbidden = False
                if getattr(obj, "rank", None) is None:
                    obj.rank = enums.RankEnum.academy

            def flush(self):
                pass

            def commit(self):
                pass

            def refresh(self, obj=None):
                pass

        app.dependency_overrides[get_db_session] = lambda: FakeSession()

        body = get_random_ninja_dict().copy()
        body.pop("id", None)
        res = client.post("/ninja", json=body)
        data = res.json()

        assert res.status_code == 201
        assert data["name"] == body["name"]
        assert data["clan"] == body["clan"]
        assert "id" in data

        app.dependency_overrides.clear()
