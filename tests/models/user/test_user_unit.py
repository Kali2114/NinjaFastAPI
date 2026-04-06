import pytest
from pydantic import ValidationError

from app.schemas.user_schema import UserCreateSchema
from app.models.utils import generate_avatar_name


@pytest.mark.unit_schema
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


@pytest.mark.unit
class TestUserUnit:

    def test_generate_avatar_name(self):
        base_name = "avatar.png"
        result = generate_avatar_name(base_name)

        assert result != base_name
        assert result.endswith(".png")
