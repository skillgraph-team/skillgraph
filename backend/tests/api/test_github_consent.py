"""Tests for GitHub consent (M3.9): the import refuses until the user agrees, and taking
consent back removes everything imported from GitHub.

GET    /profile/github-consent → {"consented_at": ... | null, "github_username": ...}
PUT    /profile/github-consent → 200, records the time of consent
DELETE /profile/github-consent → 204, withdraws it and deletes the imported repos
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.github import get_github_client
from app.config import get_settings
from app.db.models import Source
from app.main import app
from tests.api.test_profile import error_code, sign_up
from tests.fixtures.github.fake_github import FakeGitHub

CONSENT = "/profile/github-consent"


@pytest.fixture
def fake_github(tmp_path: Path) -> Iterator[FakeGitHub]:
    fake = FakeGitHub()
    cache = tmp_path / "cache"
    settings = get_settings().model_copy(update={"github_cache_dir": cache, "github_max_repos": 20})
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_github_client] = lambda: fake.client(cache)
    try:
        yield fake
    finally:
        app.dependency_overrides.pop(get_settings, None)
        app.dependency_overrides.pop(get_github_client, None)


@pytest.fixture
def student(client: TestClient, fake_github: FakeGitHub) -> TestClient:
    sign_up(client, "consent@example.com")
    return client


def import_github(client: TestClient):  # type: ignore[no-untyped-def]
    return client.post("/sources/github", json={"username": "test-student"})


def repo_count(session: Session) -> int:
    return len(session.scalars(select(Source).where(Source.kind == "github_repo")).all())


def test_no_consent_at_first(student: TestClient) -> None:
    assert student.get(CONSENT).json() == {"consented_at": None, "github_username": None}


def test_import_refuses_without_consent_and_asks_github_nothing(
    student: TestClient, db_session: Session, fake_github: FakeGitHub
) -> None:
    response = import_github(student)

    assert response.status_code == 403
    assert error_code(response) == "github_consent_required"
    assert fake_github.requests == []
    assert repo_count(db_session) == 0


def test_consent_is_recorded_and_then_the_import_works(student: TestClient) -> None:
    response = student.put(CONSENT)

    assert response.status_code == 200
    assert response.json()["consented_at"] is not None
    assert import_github(student).status_code == 200
    assert student.get(CONSENT).json()["github_username"] == "test-student"


def test_consenting_again_keeps_the_first_time(student: TestClient) -> None:
    first = student.put(CONSENT).json()["consented_at"]

    assert student.put(CONSENT).json()["consented_at"] == first


def test_withdrawing_consent_deletes_the_imported_repos_and_cache(
    student: TestClient, db_session: Session, tmp_path: Path
) -> None:
    student.put(CONSENT)
    import_github(student)
    assert repo_count(db_session) == 4
    assert list((tmp_path / "cache").iterdir())

    response = student.delete(CONSENT)

    assert response.status_code == 204
    db_session.expire_all()
    assert repo_count(db_session) == 0
    assert student.get(CONSENT).json() == {"consented_at": None, "github_username": None}
    assert list((tmp_path / "cache").iterdir()) == []
    assert error_code(import_github(student)) == "github_consent_required"


def test_withdrawing_keeps_the_cv(student: TestClient, db_session: Session) -> None:
    cv = Path(__file__).resolve().parents[1] / "fixtures" / "cv" / "cv_en.pdf"
    settings = app.dependency_overrides[get_settings]()
    app.dependency_overrides[get_settings] = lambda: settings.model_copy(
        update={"upload_dir": settings.github_cache_dir.parent / "uploads"}
    )
    student.post("/sources/cv", files={"file": ("cv.pdf", cv.read_bytes(), "application/pdf")})
    student.put(CONSENT)
    import_github(student)

    student.delete(CONSENT)

    db_session.expire_all()
    kinds = [source.kind for source in db_session.scalars(select(Source))]
    assert kinds == ["cv"]


def test_consent_needs_a_login(client: TestClient, fake_github: FakeGitHub) -> None:
    assert client.get(CONSENT).status_code == 401
    assert client.put(CONSENT).status_code == 401
    assert client.delete(CONSENT).status_code == 401
