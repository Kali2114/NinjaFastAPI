from jose import jwt
import pytest

from app.auth.hashing import hash_password, verify_password
from app.auth.token_utils import create_token, SECRET_KEY
from app.models import User


@pytest.mark.auth
class TestAuth:

    def test_register_user_successful(self, client, db_session):
        payload = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpass123",
        }
        res = client.post("/auth/register", json=payload)

        db = db_session()
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == payload["username"]
        assert data["email"] == payload["email"]
        assert "hashed_password" not in data
        user = db.query(User).filter_by(username=payload["username"]).first()
        assert user is not None

    def test_register_user_exists_fail(self, client, setup_user):
        payload = {
            "username": setup_user.username,
            "email": setup_user.email,
            "password": "testpass123",
        }
        res = client.post("/auth/register", json=payload)

        assert res.status_code == 400
        assert res.json()["detail"] == "User already exists"

    def test_login_success(self, client, setup_user):
        payload = {"username": setup_user.username, "password": "test_pass"}
        res = client.post("/auth/login", json=payload)

        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_failed(self, client):
        payload = {"username": "wrong_user", "password": "wrong_pass"}
        res = client.post("/auth/login", json=payload)

        assert res.status_code == 401
        assert res.json()["detail"] == "Invalid credentials"

    def test_hash_password_returns_different_hashes(self):
        password = "test_pass123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_hash_password_starts_with_bcrypt_prefix(self):
        password = "test_pass123"
        hashed = hash_password(password)

        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        password = "test_pass123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "test_pass123"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False

    def test_create_token_contains_payload(self):
        data = {"sub": "test_user"}
        token = create_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        assert decoded["sub"] == "test_user"
        assert "exp" in decoded
