from fastapi.testclient import TestClient
from sqlalchemy import inspect
import pytest

from app.main import app
from app.db_connection import get_db_session
from app.routers.utils import get_current_user


@pytest.fixture(scope="function")
def db_inspector(db_session):
    return inspect(db_session().bind)


@pytest.fixture(scope="function")
def client_authed(db_session, setup_user):
    session = db_session()

    def _db_override():
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise

    app.dependency_overrides[get_db_session] = _db_override
    app.dependency_overrides[get_current_user] = lambda: setup_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    session.close()
