import pytest

from app.models.ninja import Ninja
from app.db_connection import SessionLocal
from app.models import enums


class TestNinjaIntegration:

    def setup_method(self):
        self.ninja = Ninja(
            name="Naruto",
            clan="Uzumaki",
            rank=enums.RankEnum.academy,
            jinchuriki=enums.JinchurikiEnum.none,
        )
        self.session = SessionLocal()
        self.session.add(self.ninja)
        self.session.commit()
        self.session.refresh(self.ninja)

    def teardown_method(self):
        self.session.query(Ninja).delete()
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

    def test_check_level_up(self):
        self.ninja.experience = 1020
        self.ninja._check_level_up()
        assert self.ninja.level == 6

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
