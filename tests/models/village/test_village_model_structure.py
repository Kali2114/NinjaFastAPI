from sqlalchemy import Integer, Enum as SQLAEnum


class TestVillageModelExists:

    def test_table_exists(self, db_inspector):
        assert db_inspector.has_table("village")


class TestVillageModelStructure:

    def test_column_data_types(self, db_inspector):
        table = "village"
        columns = {column["name"]: column for column in db_inspector.get_columns(table)}

        assert isinstance(columns["id"]["type"], Integer)
        assert isinstance(columns["name"]["type"], SQLAEnum)
        assert isinstance(columns["country"]["type"], SQLAEnum)
        assert isinstance(columns["kage_id"]["type"], Integer)

    def test_nullable_constraints(self, db_inspector):
        table = "village"
        columns = db_inspector.get_columns(table)

        expected_nullable = {
            "id": False,
            "name": False,
            "country": False,
            "kage_id": True,
        }

        for column in columns:
            column_name = column["name"]
            assert column["nullable"] == expected_nullable.get(
                column_name
            ), f"column '{column_name}' is not nullable as expected."

    def test_unique_constraints(self, db_inspector):
        constraints = db_inspector.get_unique_constraints("village")

        assert any(constraint["name"] == "uq_kage_id" for constraint in constraints)
        assert any(
            constraint["name"] == "uq_village_name" for constraint in constraints
        )
