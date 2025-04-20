from sqlalchemy import Integer, String, Boolean, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import ARRAY


def test_model_structure_table_exists(db_inspector):
    assert db_inspector.has_table("ninja")


def test_model_structure_column_data_types(db_inspector):
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
