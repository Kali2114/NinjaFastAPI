from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
import pytest

from app.main import app
from app.routers.utils import get_current_user


@pytest.fixture(scope="function")
def db_inspector(db_session):
    return inspect(db_session().bind)


@pytest.fixture(scope="function")
def client_authed(setup_user):
    fake_user = type("UserCtx", (), {"id": setup_user.id})()

    app.dependency_overrides[get_current_user] = lambda: fake_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True, scope="function")
def _clean_db_before_test(db_session):
    s = db_session()
    try:
        s.execute(text('TRUNCATE ninja, team, "user" RESTART IDENTITY CASCADE'))
        s.commit()
    finally:
        s.close()
    yield
