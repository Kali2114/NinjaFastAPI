from sqlalchemy import Integer, String, Boolean, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import ARRAY
import pytest


class TestNinjaModelStructure:

    @pytest.mark.model
    def test_table_exists(self, db_inspector):
        assert db_inspector.has_table("ninja")

    @pytest.mark.model_structure
    def test_column_data_types(self, db_inspector):
        table = "ninja"
        columns = {column["name"]: column for column in db_inspector.get_columns(table)}

        assert isinstance(columns["id"]["type"], Integer)
        assert isinstance(columns["name"]["type"], String)
        assert isinstance(columns["clan"]["type"], String)
        assert isinstance(columns["level"]["type"], Integer)
        assert isinstance(columns["experience"]["type"], Integer)
        # assert isinstance(columns["team_id"]["type"], Integer)
        assert isinstance(columns["sensei"]["type"], String)
        assert isinstance(columns["summon_animal"]["type"], String)
        assert isinstance(columns["mission_completed"]["type"], Integer)
        # assert isinstance(columns["village_id"]["type"], Integer)
        assert isinstance(columns["rank"]["type"], SQLAEnum)
        assert isinstance(columns["kekkei_genkai"]["type"], SQLAEnum)
        assert isinstance(columns["chakra_nature"]["type"], ARRAY)
        assert isinstance(columns["alive"]["type"], Boolean)
        assert isinstance(columns["forbidden"]["type"], Boolean)
        assert isinstance(columns["jinchuriki"]["type"], SQLAEnum)

    @pytest.mark.model_structure
    def test_nullable_constraints(self, db_inspector):
        table = "ninja"
        columns = db_inspector.get_columns(table)

        expected_nullable = {
            "id": False,
            "name": False,
            "clan": False,
            "level": False,
            "experience": False,
            # "team_id": False,
            "sensei": True,
            "summon_animal": True,
            "mission_completed": False,
            # "village_id": True,
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

    @pytest.mark.model_structure
    def test_column_constraints(self, db_inspector):
        table = "ninja"
        constraints = db_inspector.get_check_constraints(table)
        expected_constraints = {
            "name_length_check",
            "clan_length_check",
            "min_1_lvl_check",
            "experience_positive_check",
            "mission_positive_check",
        }
        constraint_names = {c["name"] for c in constraints}

        assert expected_constraints.issubset(
            constraint_names
        ), f"Missing constraints {expected_constraints - constraint_names}"

    @pytest.mark.model_structure
    def test_default_values(self, db_inspector):
        table = "ninja"
        columns = {
            columns["name"]: columns for columns in db_inspector.get_columns(table)
        }

        assert columns["level"]["default"] == "1"
        assert columns["experience"]["default"] == "0"
        assert columns["mission_completed"]["default"] == "0"
        assert columns["rank"]["default"] == "'academy'::rankenum"
        assert columns["alive"]["default"] == "true"
        assert columns["forbidden"]["default"] == "false"
        assert columns["kekkei_genkai"]["default"] == "'none'::kekkeigenkaienum"
        assert columns["jinchuriki"]["default"] == "'none'::jinchurikienum"

    @pytest.mark.model_structure
    def test_column_lengths(self, db_inspector):
        table = "ninja"
        columns = {
            columns["name"]: columns for columns in db_inspector.get_columns(table)
        }

        assert columns["name"]["type"].length == 20
        assert columns["clan"]["type"].length == 20
        assert columns["sensei"]["type"].length == 20
        assert columns["summon_animal"]["type"].length == 20

    @pytest.mark.model_structure
    def test_unique_constraints(self, db_inspector):
        constraints = db_inspector.get_unique_constraints("ninja")

        assert any(constraint["name"] == "uq_ninja_name" for constraint in constraints)
