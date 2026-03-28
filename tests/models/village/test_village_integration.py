import pytest

from app.models.ninja import Ninja
from app.models.village import Village
from app.models.user import User
from app.db_connection import SessionLocal
from tests.models.utils import create_ninja, create_village, create_user
from app.models import enums


@pytest.mark.integration
class TestVillageIntegration:
    def setup_method(self):
        self.session = SessionLocal()
        self.user = create_user(self.session)
        self.konoha = create_village(session=self.session)
        self.suna = create_village(
            session=self.session,
            name=enums.VillageEnum.suna,
            country=enums.CountryEnum.wind,
        )
        self.hokage = create_ninja(
            user_id=self.user.id,
            session=self.session,
            rank=enums.RankEnum.kage,
            village_id=self.konoha.id,
        )
        self.kazekage = create_ninja(
            user_id=self.user.id,
            session=self.session,
            rank=enums.RankEnum.kage,
            village_id=self.suna.id,
        )
        self.suna.set_kage(self.kazekage)
        self.ninja_konoha = create_ninja(
            user_id=self.user.id, session=self.session, village_id=self.konoha.id
        )
        self.ninja_suna = create_ninja(
            user_id=self.user.id, session=self.session, village_id=self.suna.id
        )
        self.ninja = create_ninja(user_id=self.user.id, session=self.session)

    def teardown_method(self):
        self.session.query(Ninja).delete()
        self.session.query(User).delete()
        self.session.query(Village).delete()
        self.session.commit()
        self.session.close()

    def test_add_ninja_to_village_success(self):
        self.konoha.add_ninja_to_village(self.ninja)
        assert self.ninja in self.konoha.ninjas

    def test_add_ninja_to_village_error(self):
        with pytest.raises(ValueError):
            self.konoha.add_ninja_to_village(self.ninja_suna)

    def test_set_kage_successful(self):
        self.konoha.set_kage(self.hokage)
        self.session.flush()
        assert self.hokage.id == self.konoha.kage_id

    @pytest.mark.parametrize(
        "ninja, village, expected_error",
        [
            ("ninja_konoha", "konoha", "Only kage ninja rank"),
            ("hokage", "suna", "Only member of village"),
            ("kazekage", "suna", "Village already has a kage"),
        ],
    )
    def test_set_kage_errors(self, ninja, village, expected_error):
        with pytest.raises(ValueError, match=expected_error):
            getattr(self, village).set_kage(getattr(self, ninja))


@pytest.mark.integration
class TestVillageActionEndpointsIntegration:
    def test_get_all_villages(self, client, db_session):
        session = db_session()
        create_village(session=session)
        create_village(session=session, name=enums.VillageEnum.hoshigakure)
        session.close()

        res = client.get("/village")
        names = {village["name"] for village in res.json()}
        assert res.status_code == 200
        assert names == {"Hidden Star Village", "Hidden Leaf Village"}

    def test_get_sorted_villages_list_by_name(self, client, db_session):
        session = db_session()
        create_village(session=session)
        create_village(session=session, name=enums.VillageEnum.hoshigakure)
        create_village(session=session, name=enums.VillageEnum.uzushiogakure)
        session.close()

        res = client.get("/village/?sort_by=name")
        assert res.status_code == 200
        print(res.json())
        names = [village["name"] for village in res.json()]
        assert names == sorted(names)

    def test_get_sorted_villages_list_by_country(self, client, db_session):
        session = db_session()
        create_village(session=session)
        create_village(
            session=session, name=enums.VillageEnum.kumo, country=enums.CountryEnum.rain
        )
        create_village(
            session=session,
            name=enums.VillageEnum.suna,
            country=enums.CountryEnum.grass,
        )
        session.close()

        res = client.get("/village/?sort_by=country")
        assert res.status_code == 200
        countries = [village["country"] for village in res.json()]
        assert countries == sorted(countries)

    def test_get_detail_village(self, client, db_session):
        session = db_session()
        village = create_village(session=session)
        session.close()

        res = client.get(f"/village/{village.id}")
        assert res.status_code == 200
        assert res.json()["name"] == enums.VillageEnum.konoha.value
        assert res.json()["id"] == village.id

    def test_get_detail_village_404(self, client, db_session):
        res = client.get("/village/15")
        assert res.status_code == 404
        assert res.json() == {"detail": "Village not found"}

    def test_add_ninja_to_village(self, client_authed, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(session=session, user_id=setup_user.id)
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(
            f"/village/{village_id}/add_ninja_to_village/{ninja_id}"
        )
        assert res.status_code == 200
        assert res.json()["id"] == village_id

    def test_add_ninja_to_village_no_auth_error(self, client, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(session=session, user_id=setup_user.id)
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client.post(f"/village/{village_id}/add_ninja_to_village/{ninja_id}")
        assert res.status_code == 403
        assert res.json()["detail"] == "Not authenticated"

    def test_add_ninja_to_village_ninja_404(self, client_authed, db_session):
        session = db_session()
        village = create_village(session=session)
        village_id = village.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/add_ninja_to_village/15")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"

    def test_add_ninja_to_village_404(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(session=session, user_id=setup_user.id)
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/village/15/add_ninja_to_village/{ninja_id}")
        assert res.status_code == 404
        assert res.json()["detail"] == "Village not found"

    def test_add_ninja_to_other_village(self, client_authed, db_session, setup_user):
        session = db_session()
        v1 = create_village(session=session)
        v2 = create_village(session=session, name=enums.VillageEnum.kiri)
        ninja = create_ninja(session=session, user_id=setup_user.id, village_id=v1.id)
        v2_id = v2.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/village/{v2_id}/add_ninja_to_village/{ninja_id}")
        assert res.status_code == 409
        assert res.json()["detail"] == "Ninja already belongs to village"

    def test_add_dead_ninja_to_village(self, client_authed, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(session=session, user_id=setup_user.id)
        ninja.alive = False
        session.commit()
        session.refresh(ninja)
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(
            f"/village/{village_id}/add_ninja_to_village/{ninja_id}"
        )
        assert res.status_code == 409
        assert res.json()["detail"] == "Ninja is dead"

    def test_set_kage(self, client_authed, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.kage,
            village_id=village.id,
        )
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/set_kage/{ninja_id}")
        assert res.status_code == 200
        assert res.json()["id"] == village_id
        assert res.json()["kage_id"] == ninja_id

    def test_set_kage_no_auth(self, client, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(session=session, user_id=setup_user.id)
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client.post(f"/village/{village_id}/set_kage/{ninja_id}")
        assert res.status_code == 403
        assert res.json()["detail"] == "Not authenticated"

    def test_set_kage_dead_ninja(self, client_authed, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.kage,
            village_id=village.id,
        )
        ninja.alive = False
        session.commit()
        session.refresh(ninja)
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/set_kage/{ninja_id}")
        assert res.status_code == 409
        assert res.json()["detail"] == "Ninja is dead"

    def test_set_kage_lower_rank(self, client_authed, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.academy,
            village_id=village.id,
        )
        village_id = village.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/set_kage/{ninja_id}")
        assert res.status_code == 409
        assert res.json()["detail"] == "Only kage ninja rank can be a kage of village"

    def test_set_kage_when_have_kage(self, client_authed, db_session, setup_user):
        session = db_session()
        village = create_village(session=session)
        existing_kage = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.kage,
            village_id=village.id,
        )
        village.kage_id = existing_kage.id
        session.commit()
        session.refresh(village)
        another_kage = create_ninja(
            name="test_ninja",
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.kage,
            village_id=village.id,
        )
        village_id = village.id
        ninja_id = another_kage.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/set_kage/{ninja_id}")
        assert res.status_code == 409
        assert res.json()["detail"] == "Village already has a kage"

    def test_set_kage_from_another_village(self, client_authed, db_session, setup_user):
        session = db_session()
        v1 = create_village(session=session)
        v2 = create_village(session=session, name=enums.VillageEnum.suna)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.kage,
            village_id=v2.id,
        )
        village_id = v1.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/set_kage/{ninja_id}")
        assert res.status_code == 409
        assert res.json()["detail"] == "Only member of village can be a kage"

    def test_set_kage_ninja_not_found(self, client_authed, db_session):
        session = db_session()
        village = create_village(session=session)
        village_id = village.id
        session.close()

        res = client_authed.post(f"/village/{village_id}/set_kage/12")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"

    def test_set_kage_village_not_found(self, client_authed, db_session, setup_user):
        session = db_session()
        kage = create_ninja(
            session=session, user_id=setup_user.id, rank=enums.RankEnum.kage
        )
        kage_id = kage.id
        session.close()

        res = client_authed.post(f"/village/12/set_kage/{kage_id}")
        assert res.status_code == 404
        assert res.json()["detail"] == "Village not found"
