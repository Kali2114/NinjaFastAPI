import pytest

import random

from app.models.ninja import Ninja
from app.models.user import User
from app.db_connection import SessionLocal
from app.models import enums
from tests.models.utils import create_ninja, create_user


@pytest.mark.integration
class TestNinjaIntegration:

    def setup_method(self):
        self.session = SessionLocal()
        self.user = create_user(self.session)
        self.ninja = create_ninja(self.user.id, self.session)

    def teardown_method(self):
        self.session.query(Ninja).delete()
        self.session.query(User).delete()
        self.session.commit()
        self.session.close()

    def test_valid_chakra_nature(self):
        res = self.ninja.validate_chakra_nature("chakra_nature", ["Fire", "Water"])
        assert res == ["Fire", "Water"]

    def test_invalid_chakra_nature(self):
        with pytest.raises(ValueError) as e:
            self.ninja.validate_chakra_nature("chakra_nature", ["Fire", "Shadow"])
        assert "Invalid chakra nature(s)" in str(e.value)

    def test_experience_gained_successful(self):
        self.ninja.add_experience()
        assert self.ninja.experience > 0

    @pytest.mark.parametrize(
        "experience, expected_level",
        [
            (0, 1),
            (50, 1),
            (99, 1),
            (100, 2),
            (249, 2),
            (250, 3),
            (449, 3),
            (450, 4),
            (700, 5),
            (1020, 6),
            (3000, 10),
        ],
    )
    def test_check_level_up(self, experience, expected_level):
        self.ninja.experience = experience
        self.ninja._check_level_up()
        assert self.ninja.level == expected_level

    def test_summon_contract(self):
        animal = "Eagle"
        self.ninja.summon_contract(animal)
        assert self.ninja.summon_animal == animal

    @pytest.mark.parametrize("chakra_cost, xp_gain", [(30, 2), (40, 4), (50, 1)])
    def test_train(self, monkeypatch, chakra_cost, xp_gain):
        xp_before = self.ninja.experience
        seq = iter([chakra_cost, xp_gain])
        monkeypatch.setattr(random, "randint", lambda *args, **kwargs: next(seq))
        self.ninja.train()

        assert self.ninja.chakra == 100 - chakra_cost
        assert xp_before < self.ninja.experience <= xp_before + 4

    @pytest.mark.parametrize(
        "level, expected_chakra",
        [
            (1, 100),
            (2, 120),
            (3, 150),
            (4, 190),
            (5, 240),
            (6, 300),
            (7, 370),
            (8, 450),
            (9, 540),
            (10, 640),
        ],
    )
    def test_rest_restores_max_chakra(self, level, expected_chakra):
        self.ninja.level = level
        self.ninja.chakra = 50
        self.ninja.rest()

        assert self.ninja.chakra == expected_chakra

    def test_rest_fails_if_ninja_is_dead(self):
        self.ninja.mark_as_dead()

        with pytest.raises(RuntimeError, match="Ninja is dead"):
            self.ninja.rest()

    @pytest.mark.parametrize("lvl, expected_chakra", enums.CHAKRA_THRESHOLDS.items())
    def test_check_chakra(self, lvl, expected_chakra):
        self.ninja.level = lvl
        self.ninja._check_chakra_level()

        assert self.ninja.chakra == expected_chakra

    @pytest.mark.parametrize(
        "chakra, is_valid",
        [("Fire", True), ("Water", True), ("Shadow", False), ("Steam", False)],
    )
    def test_learn_chakra_nature(self, chakra, is_valid):
        if is_valid:
            self.ninja.learn_chakra_nature(chakra)
            assert chakra in self.ninja.chakra_nature
        else:
            with pytest.raises(ValueError, match="Invalid chakra nature"):
                self.ninja.learn_chakra_nature(chakra)

    def test_mark_as_dead(self):
        self.ninja.mark_as_dead()
        assert not self.ninja.alive

    def test_mark_as_forbidden(self):
        self.ninja.mark_as_forbidden()
        assert self.ninja.forbidden

    def test_valid_change_rank(self):
        self.ninja.change_rank("kage")
        assert self.ninja.rank == enums.RankEnum.kage

    def test_invalid_change_rank(self):
        with pytest.raises(ValueError) as e:
            self.ninja.change_rank("Error")
        assert "Invalid rank" in str(e)

    @pytest.mark.parametrize(
        "method_name, args, kwargs",
        [
            ("add_experience", (), {}),
            ("learn_chakra_nature", ("Fire",), {}),
            ("change_rank", ("kage",), {}),
        ],
    )
    def test_methods_fail_when_dead(self, method_name, args, kwargs):
        self.ninja.mark_as_dead()
        method = getattr(self.ninja, method_name)
        with pytest.raises(RuntimeError, match="Ninja is dead"):
            method(*args, **kwargs)

    def test_train_happy_path(self, client_authed, db_session, setup_user, monkeypatch):
        session = db_session()

        ninja = create_ninja(
            session=session, user_id=setup_user.id, chakra=100, experience=0, level=1
        )

        seq = iter([35, 3])
        monkeypatch.setattr(
            "app.models.ninja.random.randint", lambda *args, **kwargs: next(seq)
        )

        res = client_authed.post(f"/ninja/my_ninjas/{ninja.id}/train")
        assert res.status_code == 200

        session.refresh(ninja)
        assert ninja.chakra == 65
        assert ninja.experience == 3

    def test_train_dead_returns_409(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(
            session=session, user_id=setup_user.id, chakra=100, level=1
        )
        ninja.alive = False
        session.commit()

        res = client_authed.post(f"/ninja/my_ninjas/{ninja.id}/train")
        assert res.status_code == 409
        assert res.json()["detail"] == "Ninja is dead"

        session.refresh(ninja)
        assert ninja.experience == 0
        assert ninja.chakra == 100
        session.close()

    def test_train_not_enough_chakra_returns_400(
        self, client_authed, db_session, setup_user, monkeypatch
    ):
        session = db_session()
        ninja = create_ninja(session=session, user_id=setup_user.id, chakra=20, level=1)

        monkeypatch.setattr("app.models.ninja.random.randint", lambda *_: 40)

        res = client_authed.post(f"/ninja/my_ninjas/{ninja.id}/train")
        assert res.status_code == 400
        assert res.json()["detail"] == "Not enough chakra"

        session.refresh(ninja)
        assert ninja.experience == 0
        assert ninja.chakra == 20
        session.close()

    def test_train_not_my_ninja_returns_404(
        self, client_authed, db_session, setup_user
    ):
        session = db_session()
        other = create_user(
            session=session,
            username="Testr",
            email="test@example.com",
        )
        foreign = create_ninja(session=session, user_id=other.id, chakra=100, level=1)

        res = client_authed.post(f"/ninja/my_ninjas/{foreign.id}/train")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"
        session.close()

    def test_rest_happy_path_sets_max_chakra(
        self, client_authed, db_session, setup_user
    ):
        session = db_session()
        lvl = 4
        ninja = create_ninja(
            session=session, user_id=setup_user.id, chakra=1, level=lvl
        )

        res = client_authed.post(f"/ninja/my_ninjas/{ninja.id}/rest")
        assert res.status_code == 200

        session.refresh(ninja)
        assert ninja.chakra == enums.CHAKRA_THRESHOLDS[lvl]
        session.close()

    def test_rest_dead_returns_409(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(
            session=session, user_id=setup_user.id, chakra=100, level=1
        )
        ninja.alive = False
        session.commit()

        res = client_authed.post(f"/ninja/my_ninjas/{ninja.id}/rest")
        assert res.status_code == 409
        assert res.json()["detail"] == "Ninja is dead"

        session.refresh(ninja)
        assert ninja.chakra == 100
        session.close()

    def test_rest_not_my_ninja_returns_404(self, client_authed, db_session, setup_user):
        session = db_session()
        other = create_user(session, username="Tester", email="test@example.com")
        foreign = create_ninja(session=session, user_id=other.id, chakra=50, level=3)

        res = client_authed.post(f"/ninja/my_ninjas/{foreign.id}/rest")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"
        session.close()


@pytest.mark.endpoints
class TestNinjaEndpointsIntegration:

    def test_get_all_ninjas_public_ok(self, client, db_session, setup_user):
        session = db_session()
        u2 = create_user(session=session, username="Tester", email="tester@example.com")
        n1 = create_ninja(
            session=session, user_id=setup_user.id, name="Shika", clan="Nara"
        )
        n2 = create_ninja(session=session, user_id=u2.id, name="Kiba", clan="Inuzuka")

        res = client.get("/ninja")
        assert res.status_code == 200
        ids = {row["id"] for row in res.json()}
        assert ids.issuperset({n1.id, n2.id})
        session.close()

    def test_get_my_ninjas_ok(self, client_authed, db_session, setup_user):
        session = db_session()
        u2 = create_user(session=session, username="tester", email="tester@example.com")
        n1 = create_ninja(
            session=session, user_id=setup_user.id, name="Shika", clan="Nara"
        )
        n2 = create_ninja(
            session=session, user_id=setup_user.id, name="Kiba", clan="Inuzuka"
        )
        _ = create_ninja(session=session, user_id=u2.id, name="Shino", clan="Aburame")
        res = client_authed.get("/ninja/my_ninjas")
        ids = {row["id"] for row in res.json()}
        assert ids == {n1.id, n2.id}
        session.close()

    def test_get_my_ninja_detail_ok(self, client_authed, db_session, setup_user):
        session = db_session()
        n = create_ninja(
            session=session, user_id=setup_user.id, name="Shika", clan="Nara"
        )
        res = client_authed.get(f"/ninja/my_ninjas/{n.id}")
        assert res.status_code == 200
        assert res.json()["id"] == n.id
        session.close()

    def test_get_my_ninja_detail_404_for_other_or_missing(
        self, client_authed, db_session, setup_user
    ):
        session = db_session()
        other = create_user(
            session=session, username="tester", email="test@example.com"
        )
        foreign = create_ninja(
            session=session, user_id=other.id, name="Neji", clan="Hyuga"
        )

        res1 = client_authed.get(f"/ninja/my_ninjas/{foreign.id}")
        assert res1.status_code == 404
        assert res1.json()["detail"] == "Ninja not found"

        res2 = client_authed.get("/ninja/my_ninjas/999999")
        assert res2.status_code == 404
        session.close()

    def test_create_ninja_logged_user(self, client_authed, db_session, setup_user):
        session = db_session()
        payload = {"name": "test", "clan": "testers"}

        res = client_authed.post("/ninja", json=payload)
        assert res.status_code == 201
        assert res.json()["name"] == payload["name"]
        assert res.json()["clan"] == payload["clan"]
        session.close()

    def test_delete_my_ninja_204_and_gone(self, client_authed, db_session, setup_user):
        session = db_session()
        n = create_ninja(
            session=session,
            user_id=setup_user.id,
            name="Isso",
            clan="X",
        )
        idx = n.id
        res = client_authed.delete(f"/ninja/my_ninjas/{n.id}")
        assert res.status_code == 204
        session.expire_all()
        assert db_session().get(Ninja, idx) is None

    def test_delete_other_ninja_404(self, client_authed, db_session, setup_user):
        session = db_session()
        other = create_user(session=session, username="tester", email="tester@info.com")
        n = create_ninja(session=session, user_id=other.id, name="Sussy", clan="X")

        res = client_authed.delete(f"/ninja/my_ninjas/{n.id}")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"
        session.close()
