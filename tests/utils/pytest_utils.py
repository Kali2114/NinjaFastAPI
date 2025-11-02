import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        if item.cls:
            cls_name = item.cls.__name__.lower()
            if "exists" in cls_name:
                item.add_marker(pytest.mark.exists)
            if "structure" in cls_name:
                item.add_marker(pytest.mark.structure)
            if "integration" in cls_name:
                item.add_marker(pytest.mark.integration)
            if "unit" in cls_name:
                item.add_marker(pytest.mark.unit)
            if "unitschema" in cls_name:
                item.add_marker(pytest.mark.unit_schema)
            if "endpoints" in cls_name:
                item.add_marker(pytest.mark.endpoints)
