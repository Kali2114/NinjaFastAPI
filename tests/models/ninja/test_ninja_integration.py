import pytest

import random

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
        self.ninja.chakra = expected_chakra

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
