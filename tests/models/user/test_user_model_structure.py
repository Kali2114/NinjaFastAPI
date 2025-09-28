from sqlalchemy import Integer, String, Boolean, DateTime
import pytest


@pytest.mark.exists
class UserModelExists:

    def test_table_exists(self, db_inspector):
        assert db_inspector.has_table("user")


@pytest.mark.structure
class TestUserModelStructure:
    table = "user"

    def test_column_data_types(self, db_inspector):
        columns = {
            column["name"]: column for column in db_inspector.get_columns(self.table)
        }

        assert isinstance(columns["id"]["type"], Integer)
        assert isinstance(columns["username"]["type"], String)
        assert isinstance(columns["email"]["type"], String)
        assert isinstance(columns["hashed_password"]["type"], String)
        assert isinstance(columns["is_active"]["type"], Boolean)
        assert isinstance(columns["created_at"]["type"], DateTime)

    def test_nullable_constraints(self, db_inspector):
        columns = db_inspector.get_columns(self.table)

        for column in columns:
            assert column["nullable"] is False

    def test_column_constraints(self, db_inspector):
        constraints = db_inspector.get_check_constraints(self.table)
        expected_constraints = {
            "username_length_check",
            "email_length_check",
            "password_length_check",
        }
        constraint_names = {c["name"] for c in constraints}

        assert expected_constraints.issubset(
            constraint_names
        ), f"Missing constraints {expected_constraints - constraint_names}"

    def test_default_values(self, db_inspector):
        columns = {
            columns["name"]: columns for columns in db_inspector.get_columns(self.table)
        }

        assert columns["is_active"]["default"] == "true"

    def test_column_lengths(self, db_inspector):
        columns = {
            column["name"]: column for column in db_inspector.get_columns(self.table)
        }

        assert columns["username"]["type"].length == 50

    def test_unique_constraints(self, db_inspector):
        constraints = db_inspector.get_unique_constraints(self.table)

        assert any(constraint["name"] == "uq_username" for constraint in constraints)
        assert any(constraint["name"] == "uq_email" for constraint in constraints)
