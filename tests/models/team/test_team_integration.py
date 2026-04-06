import pytest

from app.db_connection import SessionLocal
from app.models.team import Team
from app.models.ninja import enums
from tests.models.utils import create_ninja, create_user, create_team


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
            ("set_academy_as_sensei", "team1", "Academy students cannot join a team"),
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
            ("add_sensei_as_member", "Sensei cannot be a regular member"),
            ("add_academy_student", "Academy students cannot join a team"),
        ],
    )
    def test_add_ninja_errors(self, setup_fn, expected_error):
        getattr(self, setup_fn)()

        with pytest.raises(ValueError, match=expected_error):
            self.team1.add_ninja(self.ninja_to_add)


@pytest.mark.integration
class TestTeamActionEndpointsIntegration:
    def test_get_all_teams(self, client, db_session):
        session = db_session()
        create_team(session=session)
        create_team(session=session, name="Team 2")
        session.close()

        res = client.get("/team")
        names = {team["name"] for team in res.json()}
        assert res.status_code == 200
        assert names == {"Team 7", "Team 2"}

    def test_get_sorted_teams_by_name(self, client, db_session):
        session = db_session()
        create_team(session=session)
        create_team(session=session, name="Team 2")
        create_team(session=session, name="Team 8")
        create_team(session=session, name="Anaconda Team")
        create_team(session=session, name="Nightmare Team")
        session.close()

        res = client.get("/team/?sort_by=name")
        assert res.status_code == 200
        names = [team["name"] for team in res.json()]
        assert names == sorted(names)

    def test_get_all_teams_filtered_by_sensei(self, client, db_session, setup_user):
        session = db_session()
        create_team(session=session)
        create_team(session=session, name="Team 2")
        create_team(session=session, name="Team 8")
        create_team(session=session, name="Anaconda Team")
        sensei = create_ninja(
            session=session, user_id=setup_user.id, rank=enums.RankEnum.jonin
        )
        create_team(session=session, name="Nightmare Team", sensei_id=sensei.id)
        sensei_name = sensei.name
        sensei_id = sensei.id
        session.close()

        res = client.get(f"/team/?sensei_id={sensei_id}")
        assert res.status_code == 200
        assert res.json()[0]["sensei"]["name"] == sensei_name

    def test_get_all_teams_return_10_items_on_first_page(self, client, db_session):
        session = db_session()
        for t in range(12):
            create_team(session=session, name=f"Team{t}")
        session.close()

        res = client.get("/team/?page=1")
        assert res.status_code == 200
        assert len(res.json()) == 10

    def test_get_all_teams_return_2_items_on_second_page(self, client, db_session):
        session = db_session()
        for t in range(12):
            create_team(session=session, name=f"Team{t}")
        session.close()

        res = client.get("/team/?page=2")
        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_get_all_teams_return_empty_list_on_second_page_with_10_items(
        self, client, db_session
    ):
        session = db_session()
        for t in range(10):
            create_team(session=session, name=f"Team{t}")
        session.close()

        res = client.get("/team/?page=2")
        assert res.status_code == 200
        assert res.json() == []

    def test_get_all_ninjas_return_422_when_page_is_zero(self, client, db_session):
        res = client.get("/team/?page=0")
        assert res.status_code == 422
        assert (
            res.json()["detail"][0]["msg"]
            == "Input should be greater than or equal to 1"
        )

    def test_get_all_ninjas_return_422_when_page_is_negative(self, client):
        res = client.get("/team/?page=-1")
        assert res.status_code == 422
        assert (
            res.json()["detail"][0]["msg"]
            == "Input should be greater than or equal to 1"
        )

    def test_get_all_ninjas_return_422_when_page_is_not_integer(self, client):
        res = client.get("/team/?page=abc")
        assert res.status_code == 422
        assert (
            res.json()["detail"][0]["msg"]
            == "Input should be a valid integer, unable to parse string as an integer"
        )

    def test_get_detail_team(self, client, db_session):
        session = db_session()
        t1 = create_team(session=session)
        session.close()

        res = client.get(f"/team/{t1.id}")
        assert res.status_code == 200
        assert res.json()["name"] == t1.name
        assert res.json()["id"] == t1.id

    def test_get_detail_team_404(self, client, db_session):
        res = client.get("/team/15")
        assert res.status_code == 404
        assert res.json()["detail"] == "Team not found"

    def test_create_team_with_kage(self, client_authed, db_session, setup_user):
        session = db_session()
        create_ninja(session=session, user_id=setup_user.id, rank=enums.RankEnum.kage)
        session.close()

        res = client_authed.post("/team", json={"name": "Team 7"})
        assert res.status_code == 201
        assert res.json()["name"] == "Team 7"

    def test_create_team_without_kage(self, client_authed, db_session, setup_user):

        res = client_authed.post("/team", json={"name": "Team 7"})
        assert res.status_code == 403
        assert res.json()["detail"] == "Only kage can create teams"

    def test_duplicate_team(self, client_authed, db_session, setup_user):
        session = db_session()
        create_team(session=session)
        create_ninja(session=session, user_id=setup_user.id, rank=enums.RankEnum.kage)
        session.close()

        res = client_authed.post("/team", json={"name": "Team 7"})
        assert res.status_code == 409
        assert res.json()["detail"] == "Duplicate"

    def test_patch_team_forbidden(self, client_authed, db_session):
        session = db_session()
        ti = create_team(session=session)
        session.close()

        res = client_authed.patch(f"/team/{ti.id}")
        assert res.status_code == 403
        assert res.json()["detail"] == "Editing teams is not allowed"

    def test_delete_team_forbidden(self, client_authed, db_session):
        session = db_session()
        ti = create_team(session=session)
        session.close()

        res = client_authed.delete(f"/team/{ti.id}")
        assert res.status_code == 403
        assert res.json()["detail"] == "Deleting teams is not allowed"

    def test_set_sensei_ok(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(
            session=session, user_id=setup_user.id, rank=enums.RankEnum.jonin
        )
        team = create_team(session=session)
        ninja_id = ninja.id
        team_id = team.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/sensei/{ninja_id}")
        assert res.status_code == 200
        assert res.json()["sensei"]["id"] == ninja_id
        assert res.json()["id"] == team_id

    def test_set_sensei_no_jonin_error(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(
            session=session, user_id=setup_user.id, rank=enums.RankEnum.genin
        )
        team = create_team(session=session)
        ninja_id = ninja.id
        team_id = team.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/sensei/{ninja_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "Only jonin can be a sensei"

    def test_set_member_sensei_error(self, client_authed, db_session, setup_user):
        session = db_session()
        team = create_team(session=session)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            team_id=team.id,
            rank=enums.RankEnum.jonin,
        )
        team_id = team.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/sensei/{ninja_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "Ninja is already a member of a team"

    def test_set_sensei_second_team_error(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.jonin,
        )
        create_team(session=session, sensei_id=ninja.id)
        t2 = create_team(name="Team 55", session=session)
        ninja_id = ninja.id
        t2_id = t2.id
        session.close()

        res = client_authed.post(f"/team/{t2_id}/sensei/{ninja_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "Ninja is already a sensei of another team"

    def test_sensei_not_found_error(self, client_authed, db_session, setup_user):
        session = db_session()
        team = create_team(session=session)
        team_id = team.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/sensei/24")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"

    def test_team_not_found_error(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(session=session, user_id=setup_user.id)
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/team/34/sensei/{ninja_id}")
        assert res.status_code == 404
        assert res.json()["detail"] == "Team not found"

    def test_add_ninja_ok(self, client_authed, db_session, setup_user):
        session = db_session()
        team = create_team(session=session)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.genin,
        )
        team_id = team.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/members/{ninja_id}")
        assert res.status_code == 200
        assert res.json()["id"] == team_id
        assert any(member["id"] == ninja_id for member in res.json()["members"])

    def test_add_ninja_fourth_member_error(self, client_authed, db_session, setup_user):
        session = db_session()
        team = create_team(session=session)
        create_ninja(session=session, user_id=setup_user.id, team_id=team.id)
        create_ninja(session=session, user_id=setup_user.id, team_id=team.id, name="N2")
        create_ninja(session=session, user_id=setup_user.id, team_id=team.id, name="N3")
        ninja4 = create_ninja(session=session, user_id=setup_user.id, name="N4")
        team_id = team.id
        ninja4_id = ninja4.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/members/{ninja4_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "Team already has 3 members"

    def test_add_ninja_sensei_error(self, client_authed, db_session, setup_user):
        session = db_session()
        sensei = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.jonin,
        )
        team = create_team(session=session, sensei_id=sensei.id)
        team_id = team.id
        sensei_id = sensei.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/members/{sensei_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "Sensei cannot be a regular member"

    def test_add_ninja_academy_error(self, client_authed, db_session, setup_user):
        session = db_session()
        team = create_team(session=session)
        ninja = create_ninja(
            session=session,
            user_id=setup_user.id,
            rank=enums.RankEnum.academy,
        )
        team_id = team.id
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/members/{ninja_id}")
        assert res.status_code == 400
        assert res.json()["detail"] == "Academy students cannot join a team"

    def test_add_ninja_team_not_found(self, client_authed, db_session, setup_user):
        session = db_session()
        ninja = create_ninja(session=session, user_id=setup_user.id)
        ninja_id = ninja.id
        session.close()

        res = client_authed.post(f"/team/9999/members/{ninja_id}")
        assert res.status_code == 404
        assert res.json()["detail"] == "Team not found"

    def test_add_ninja_ninja_not_found(self, client_authed, db_session):
        session = db_session()
        team = create_team(session=session)
        team_id = team.id
        session.close()

        res = client_authed.post(f"/team/{team_id}/members/9999")
        assert res.status_code == 404
        assert res.json()["detail"] == "Ninja not found"
