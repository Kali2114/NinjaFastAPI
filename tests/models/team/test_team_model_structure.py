from sqlalchemy import Integer, String


class TestTeamModelExists:

    def test_table_exists(self, db_inspector):
        assert db_inspector.has_table("team")


class TestTeamModelStructure:
    table = "team"

    def test_column_data_types(self, db_inspector):
        columns = {
            column["name"]: column for column in db_inspector.get_columns(self.table)
        }

        assert isinstance(columns["id"]["type"], Integer)
        assert isinstance(columns["name"]["type"], String)
        assert isinstance(columns["sensei_id"]["type"], Integer)

    def test_nullable_constraints(self, db_inspector):
        columns = db_inspector.get_columns(self.table)

        expected_nullable = {
            "id": False,
            "name": False,
            "sensei_id": True,
        }

        for column in columns:
            column_name = column["name"]
            assert column["nullable"] == expected_nullable.get(
                column_name
            ), f"column '{column_name}' is not nullable as expected."

    def test_column_lengths(self, db_inspector):
        columns = {
            column["name"]: column for column in db_inspector.get_columns(self.table)
        }

        assert columns["name"]["type"].length == 20

    def test_unique_constraints(self, db_inspector):
        constraints = db_inspector.get_unique_constraints(self.table)

        assert any(constraint["name"] == "uq_team_name" for constraint in constraints)
        assert any(constraint["name"] == "uq_sensei_id" for constraint in constraints)
