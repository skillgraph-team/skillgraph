"""Tests for listing and deleting sources (M3.7, for the sources screen).

GET    /sources       → 200 the user's sources, newest first, without their text
DELETE /sources/{id}  → 204; a CV's file is deleted with it
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import User
from app.main import app
from tests.api.test_profile import error_code, log_in, sign_up
from tests.api.test_sources import FIXTURES, stored_files, upload
from tests.db import factories as f


@pytest.fixture
def upload_dir(tmp_path: Path) -> Iterator[Path]:
    folder = tmp_path / "uploads"
    settings = get_settings().model_copy(update={"upload_dir": folder})
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        yield folder
    finally:
        app.dependency_overrides.pop(get_settings, None)


def upload_cv(client: TestClient, name: str = "cv.pdf") -> str:
    response = upload(client, name, (FIXTURES / "cv_en.pdf").read_bytes())
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def test_list_is_empty_at_first(client: TestClient, upload_dir: Path) -> None:
    sign_up(client, "list@example.com")
    assert client.get("/sources").json() == []


def test_list_is_newest_first(client: TestClient, db_session: Session) -> None:
    sign_up(client, "list@example.com")
    user = db_session.scalars(select(User)).one()
    # Set the times: inside one test transaction the database's now() never moves.
    for title, day in [("old.pdf", 1), ("test-student/shop-api", 3), ("new.pdf", 2)]:
        f.make_source(db_session, user, title=title, created_at=datetime(2026, 11, day, tzinfo=UTC))
    db_session.commit()

    titles = [source["title"] for source in client.get("/sources").json()]

    assert titles == ["test-student/shop-api", "new.pdf", "old.pdf"]


def test_list_gives_a_summary_without_the_text(
    client: TestClient, db_session: Session, upload_dir: Path
) -> None:
    sign_up(client, "list@example.com")
    upload_cv(client, "cv.pdf")
    user = db_session.scalars(select(User)).one()
    f.make_source(
        db_session,
        user,
        kind="github_repo",
        title="test-student/shop-api",
        text="# README",
        details={"html_url": "https://github.com/test-student/shop-api", "readme": "big"},
    )
    db_session.commit()

    sources = {source["kind"]: source for source in client.get("/sources").json()}

    assert set(sources["cv"]) == {"id", "kind", "title", "language", "url", "created_at"}
    assert sources["cv"]["title"] == "cv.pdf"
    assert sources["cv"]["language"] == "en"
    assert sources["cv"]["url"] is None
    assert sources["github_repo"]["url"] == "https://github.com/test-student/shop-api"


def test_list_shows_only_the_users_own_sources(client: TestClient, upload_dir: Path) -> None:
    sign_up(client, "first@example.com")
    upload_cv(client)
    sign_up(client, "second@example.com")
    log_in(client, "second@example.com")

    assert client.get("/sources").json() == []


def test_deleting_a_cv_removes_its_row_and_file(
    client: TestClient, db_session: Session, upload_dir: Path
) -> None:
    sign_up(client, "delete@example.com")
    source_id = upload_cv(client)
    kept = upload_cv(client, "kept.pdf")
    assert len(stored_files(upload_dir)) == 2

    response = client.delete(f"/sources/{source_id}")

    assert response.status_code == 204
    assert [source["id"] for source in client.get("/sources").json()] == [kept]
    assert len(stored_files(upload_dir)) == 1


def test_cannot_delete_someone_elses_source(client: TestClient, upload_dir: Path) -> None:
    sign_up(client, "owner@example.com")
    source_id = upload_cv(client)
    sign_up(client, "other@example.com")
    log_in(client, "other@example.com")

    response = client.delete(f"/sources/{source_id}")

    assert response.status_code == 404
    assert error_code(response) == "not_found"
    assert len(stored_files(upload_dir)) == 1


def test_deleting_an_unknown_source_is_not_found(client: TestClient, upload_dir: Path) -> None:
    sign_up(client, "delete@example.com")
    response = client.delete("/sources/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_sources_need_a_login(client: TestClient) -> None:
    assert client.get("/sources").status_code == 401
    assert client.delete("/sources/00000000-0000-0000-0000-000000000000").status_code == 401
