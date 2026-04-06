import pytest
from pydantic import ValidationError
import os
from io import BytesIO

from app.schemas.user_schema import UserCreateSchema
from app.models.utils import (
    generate_avatar_name,
    validate_avatar,
    save_avatar_in_storage,
)


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

    @pytest.mark.parametrize(
        "filename, should_raise",
        [
            ("avatar.png", False),
            ("photo.jpg", False),
            ("image.jpeg", False),
            ("file.txt", True),
            ("", True),
        ],
    )
    def test_validate_avatar(self, filename, should_raise):
        class FakeFile:
            def __init__(self, filename):
                self.filename = filename

        file = FakeFile(filename)
        if should_raise:
            with pytest.raises(ValueError):
                validate_avatar(file)
        else:
            validate_avatar(file)

    def test_save_avatar_in_storage(self):
        content = b"fake image content"

        class FakeUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.file = BytesIO(content)

        file = FakeUploadFile("avatar.png", content)

        os.makedirs(os.path.join("media", "avatars"), exist_ok=True)

        result = save_avatar_in_storage(file)

        saved_path = os.path.join("media", "avatars", result)

        assert result.endswith(".png")
        assert os.path.exists(saved_path)

        with open(saved_path, "rb") as saved_file:
            saved_content = saved_file.read()

        assert saved_content == content

        os.remove(saved_path)
