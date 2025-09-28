from sqlalchemy import Integer, String, Boolean, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import ARRAY
import pytest


@pytest.mark.exists
class TestNinjaModelExists:

    def test_table_exists(self, db_inspector):
        assert db_inspector.has_table("ninja")


@pytest.mark.structure
class TestNinjaModelStructure:
    table = "ninja"

    def test_column_data_types(self, db_inspector):
        columns = {
            column["name"]: column for column in db_inspector.get_columns(self.table)
        }

        assert isinstance(columns["id"]["type"], Integer)
        assert isinstance(columns["name"]["type"], String)
        assert isinstance(columns["chakra"]["type"], Integer)
        assert isinstance(columns["clan"]["type"], String)
        assert isinstance(columns["level"]["type"], Integer)
        assert isinstance(columns["experience"]["type"], Integer)
        assert isinstance(columns["team_id"]["type"], Integer)
        assert isinstance(columns["sensei"]["type"], String)
        assert isinstance(columns["summon_animal"]["type"], String)
        assert isinstance(columns["mission_completed"]["type"], Integer)
        assert isinstance(columns["village_id"]["type"], Integer)
        assert isinstance(columns["user_id"]["type"], Integer)
        assert isinstance(columns["rank"]["type"], SQLAEnum)
        assert isinstance(columns["kekkei_genkai"]["type"], SQLAEnum)
        assert isinstance(columns["chakra_nature"]["type"], ARRAY)
        assert isinstance(columns["alive"]["type"], Boolean)
        assert isinstance(columns["forbidden"]["type"], Boolean)
        assert isinstance(columns["jinchuriki"]["type"], SQLAEnum)

    def test_nullable_constraints(self, db_inspector):
        columns = db_inspector.get_columns(self.table)

        expected_nullable = {
            "id": False,
            "name": False,
            "chakra": False,
            "clan": False,
            "level": False,
            "experience": False,
            "team_id": True,
            "team": False,
            "sensei": True,
            "summon_animal": True,
            "mission_completed": False,
            "village_id": True,
            "user_id": False,
            "rank": False,
            "kekkei_genkai": True,
            "chakra_nature": True,
            "alive": False,
            "forbidden": False,
            "jinchuriki": False,
        }

        for column in columns:
            column_name = column["name"]
            assert column["nullable"] == expected_nullable.get(
                column_name
            ), f"column '{column_name}' is not nullable as expected."

    def test_column_constraints(self, db_inspector):
        constraints = db_inspector.get_check_constraints(self.table)
        expected_constraints = {
            "name_length_check",
            "chakra_check",
            "clan_length_check",
            "min_1_lvl_check",
            "experience_positive_check",
            "mission_positive_check",
        }
        constraint_names = {c["name"] for c in constraints}

        assert expected_constraints.issubset(
            constraint_names
        ), f"Missing constraints {expected_constraints - constraint_names}"

    def test_default_values(self, db_inspector):
        columns = {
            columns["name"]: columns for columns in db_inspector.get_columns(self.table)
        }

        assert columns["chakra"]["default"] == "100"
        assert columns["level"]["default"] == "1"
        assert columns["experience"]["default"] == "0"
        assert columns["mission_completed"]["default"] == "0"
        assert columns["rank"]["default"] == "'academy'::rankenum"
        assert columns["alive"]["default"] == "true"
        assert columns["forbidden"]["default"] == "false"
        assert columns["kekkei_genkai"]["default"] == "'none'::kekkeigenkaienum"
        assert columns["jinchuriki"]["default"] == "'none'::jinchurikienum"

    def test_column_lengths(self, db_inspector):
        columns = {
            columns["name"]: columns for columns in db_inspector.get_columns(self.table)
        }

        assert columns["name"]["type"].length == 20
        assert columns["clan"]["type"].length == 20
        assert columns["sensei"]["type"].length == 20
        assert columns["summon_animal"]["type"].length == 20

    def test_unique_constraints(self, db_inspector):
        constraints = db_inspector.get_unique_constraints(self.table)

        assert any(constraint["name"] == "uq_ninja_name" for constraint in constraints)
