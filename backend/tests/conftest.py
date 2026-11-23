"""Shared test fixtures: a separate test database, and a session whose changes are undone.

How it works:
- `test_engine` connects to TEST_DATABASE_URL (never DATABASE_URL, so your development
  data is never touched) and brings it up to date by running every migration once.
- `db_session` opens a transaction for one test and rolls it back afterwards, so each
  test starts from the same empty database, even if the code under test calls commit().
- `client` is a FastAPI test client whose endpoints use that same `db_session`.

Tests that use any of these need the database running: `docker compose up -d db`.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_session
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    # migrations/env.py uses this URL instead of DATABASE_URL when it is set.
    config.set_main_option("sqlalchemy.url", get_settings().test_database_url)
    return config


@pytest.fixture(scope="session")
def test_engine(alembic_config: Config) -> Iterator[Engine]:
    engine = create_engine(get_settings().test_database_url)
    command.upgrade(alembic_config, "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    connection = test_engine.connect()
    transaction = connection.begin()
    # "create_savepoint": a commit() inside the code under test only ends a savepoint,
    # so the rollback below still undoes everything the test did.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
