"""Tests for app/main.py: the health endpoint reports the server and the database."""

from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.main import app


def test_health_ok_when_database_reachable(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_reports_unreachable_database() -> None:
    class BrokenSession:
        def execute(self, *args: object, **kwargs: object) -> None:
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    def broken_session() -> Iterator[BrokenSession]:
        yield BrokenSession()

    app.dependency_overrides[get_session] = broken_session
    try:
        response = TestClient(app).get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unreachable"}


def test_session_fixture_is_on_test_database(db_session: Session) -> None:
    name = db_session.execute(text("SELECT current_database()")).scalar_one()

    assert name.endswith("_test")
