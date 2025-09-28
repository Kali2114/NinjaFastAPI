import pytest

from app.db_connection import SessionLocal
from app.models.team import Team
from app.models.ninja import Ninja
from app.models.user import User
from app.models.ninja import enums
from tests.models.utils import create_ninja, create_user


@pytest.mark.integration
class TestTeamIntegration:

    def setup_method(self):
        self.session = SessionLocal()
        self.user = create_user(self.session)
        self.ninjas = [create_ninja(self.user.id, self.session) for _ in range(4)]
        self.academy = create_ninja(
            self.user.id, self.session, rank=enums.RankEnum.academy
        )
        self.sensei = create_ninja(
            self.user.id, self.session, rank=enums.RankEnum.jonin
        )

        self.ninjas.extend([self.academy, self.sensei])

        self.team1 = Team(name="test_team_1")
        self.team2 = Team(name="test_team_2")

        self.session.add_all([self.team1, self.team2])
        self.session.commit()

    def teardown_method(self):
        self.session.query(Ninja).delete()
        self.session.query(User).delete()
        self.session.query(Team).delete()

        self.session.commit()
        self.session.close()

    def add_same_twice(self):
        self.ninja_to_add = self.ninjas[0]
        self.team1.add_ninja(self.ninja_to_add)

    def add_fourth_member(self):
        self.team1.add_ninja(self.ninjas[0])
        self.team1.add_ninja(self.ninjas[1])
        self.team1.add_ninja(self.ninjas[2])
        self.ninja_to_add = self.ninjas[3]

    def add_sensei_as_member(self):
        self.team1.set_sensei(self.sensei, self.session)
        self.ninja_to_add = self.sensei

    def add_academy_student(self):
        self.ninja_to_add = self.academy

    def add_as_member_then_sensei(self):
        self.team1.add_ninja(self.sensei)

    def set_as_sensei_then_again(self):
        self.team1.set_sensei(self.sensei, self.session)

    def set_as_sensei_another_team(self):
        self.team2.set_sensei(self.sensei, self.session)

    def set_academy_as_sensei(self):
        self.sensei = self.academy

    def test_set_sensei_successful(self):
        self.team1.set_sensei(self.sensei, self.session)

        assert self.team1.sensei == self.sensei

    @pytest.mark.parametrize(
        "setup_fn, target_team, expected_error",
        [
            ("add_as_member_then_sensei", "team1", "already a member"),
            ("set_as_sensei_then_again", "team1", "already a sensei"),
            ("set_academy_as_sensei", "team1", "Academy students cannot join a team."),
            ("set_as_sensei_another_team", "team2", "already a sensei"),
        ],
    )
    def test_set_sensei_errors(self, setup_fn, target_team, expected_error):
        getattr(self, setup_fn)()

        with pytest.raises(ValueError, match=expected_error):
            getattr(self, target_team).set_sensei(self.sensei, self.session)

    def test_add_team_member_successful(self):
        self.team1.add_ninja(self.ninjas[0])

        assert len(self.team1.members) > 0

    @pytest.mark.parametrize(
        "setup_fn, expected_error",
        [
            ("add_same_twice", "already a member"),
            ("add_fourth_member", "already has 3 members"),
            ("add_sensei_as_member", "Sensei cannot be a regular member."),
            ("add_academy_student", "Academy students cannot join a team."),
        ],
    )
    def test_add_ninja_errors(self, setup_fn, expected_error):
        getattr(self, setup_fn)()

        with pytest.raises(ValueError, match=expected_error):
            self.team1.add_ninja(self.ninja_to_add)
