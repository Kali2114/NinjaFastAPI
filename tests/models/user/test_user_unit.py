import pytest
from pydantic import ValidationError

from app.schemas.user_schema import UserCreateSchema


class TestUserUnitSchema:

    def test_user_schema_validation(self):
        valid_data = {
            "username": "TestName",
            "email": "example@test.com",
            "password": "Testpass123",
        }
        user = UserCreateSchema(**valid_data)
        assert user.username == valid_data["username"]
        assert user.email == valid_data["email"]
        assert user.password == valid_data["password"]

        invalid_data = {
            "username": "TestName",
            "email": "example@test.com",
        }
        with pytest.raises(ValidationError):
            UserCreateSchema(**invalid_data)

        too_short = {"username": "abc", "email": "a@b.c", "password": "123"}
        with pytest.raises(ValidationError):
            UserCreateSchema(**too_short)

        bad_email = {
            "username": "abc",
            "email": "not-an-email",
            "password": "GoodPass123",
        }
        with pytest.raises(ValidationError):
            UserCreateSchema(**bad_email)
