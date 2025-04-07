import pytest

from tests.utils.docker_utils import start_database_container


@pytest.fixture(scope="session", autouse=True)
def db_session():
    container = start_database_container()
    yield
    container.stop()
    container.remove()
