import pytest

from app.models.ninja import Ninja
from app.models.village import Village
from app.db_connection import SessionLocal
from tests.models.utils import create_ninja, create_village
from app.models import enums


class TestVillageIntegration:

    def setup_method(self):
        self.session = SessionLocal()
        self.konoha = create_village(session=self.session)
        self.suna = create_village(
            session=self.session,
            name=enums.VillageEnum.suna,
            country=enums.CountryEnum.wind,
        )
        self.hokage = create_ninja(
            session=self.session, rank=enums.RankEnum.kage, village_id=self.konoha.id
        )
        self.kazekage = create_ninja(
            session=self.session, rank=enums.RankEnum.kage, village_id=self.suna.id
        )
        self.suna.set_kage(self.kazekage)
        self.ninja_konoha = create_ninja(
            session=self.session, village_id=self.konoha.id
        )
        self.ninja_suna = create_ninja(session=self.session, village_id=self.suna.id)
        self.ninja = create_ninja(session=self.session)

    def teardown_method(self):
        self.session.query(Ninja).delete()
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
