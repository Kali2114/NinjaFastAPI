import pytest

from app.models.user import User


@pytest.mark.integration
class TestUserModelEndpointsIntegration:

    def test_add_avatar_to_user(self, db_session, client_authed, setup_user):
        files = {"avatar": ("avatar.png", b"fake avatar", "image/png")}

        res = client_authed.post("/auth/me/avatar", files=files)
        session = db_session()
        user_id = setup_user.id
        user = session.query(User).filter(User.id == user_id).first()
        session.close()

        assert res.status_code == 200
        assert user.avatar_filename is not None

    def test_add_avatar_to_user_wrong_extension(
        self, db_session, client_authed, setup_user
    ):
        files = {"avatar": ("avatar.txt", b"fake avatar", "text/plain")}

        res = client_authed.post("/auth/me/avatar", files=files)
        session = db_session()
        user_id = setup_user.id
        user = session.query(User).filter(User.id == user_id).first()
        session.close()

        assert res.status_code == 400
        assert user.avatar_filename is None
        assert res.json()["detail"] == "Invalid file extension"

    def test_add_avatar_to_user_requires_authentication(self, db_session, client):
        files = {"avatar": ("avatar.png", b"fake avatar", "image/png")}

        res = client.post("/auth/me/avatar", files=files)
        assert res.status_code == 401
        print(res.json())
        assert res.json()["detail"] == "Authentication credentials were not provided"

    def test_add_avatar_to_user_without_file(
        self, db_session, client_authed, setup_user
    ):
        res = client_authed.post("/auth/me/avatar")

        print(res.json())
        assert res.status_code == 400
        assert res.json()["detail"] == "Invalid file extension"

    def test_add_avatar_to_user_accept_uppercase_extension(
        self, db_session, client_authed, setup_user
    ):
        files = {"avatar": ("avatar.PNG", b"fake avatar", "image/png")}

        res = client_authed.post("/auth/me/avatar", files=files)
        session = db_session()
        user_id = setup_user.id
        user = session.query(User).filter(User.id == user_id).first()
        session.close()

        assert res.status_code == 200
        assert user.avatar_filename is not None

    def test_add_another_avatar_to_user(self, db_session, client_authed, setup_user):
        files1 = {"avatar": ("avatar.png", b"fake avatar", "image/png")}

        files2 = {"avatar": ("avengers.png", b"fake avatar", "image/png")}

        client_authed.post("/auth/me/avatar", files=files1)
        session = db_session()
        user_id = setup_user.id
        user = session.query(User).filter(User.id == user_id).first()
        old_avatar = user.avatar_filename
        session.close()

        res = client_authed.post("/auth/me/avatar", files=files2)

        session = db_session()
        updated_user = session.query(User).filter(User.id == user_id).first()
        new_avatar = updated_user.avatar_filename
        session.close()

        assert res.status_code == 200
        assert old_avatar != new_avatar
        assert new_avatar is not None
        assert new_avatar.endswith(".png")
