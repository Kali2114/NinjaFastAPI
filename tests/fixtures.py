import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os

from tests.utils.docker_utils import start_database_container
from tests.utils.database_utils import migrate_to_db
from tests.factories.models_factory import create_test_user
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def db_session():
    start_database_container()
    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin() as connection:
        migrate_to_db("migrations", "alembic.ini", connection)

    session_local = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    yield session_local

    # container.stop()
    # container.remove()
    engine.dispose()


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as _client:
        yield _client


@pytest.fixture(scope="function")
def setup_user(db_session):
    db = db_session()
    user = create_test_user(db)
    db.commit()
    db.refresh(user)
    db.close()
    return user
