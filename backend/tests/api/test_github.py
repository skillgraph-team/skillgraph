"""Tests for GitHub import (M3.6): `POST /sources/github` stores one `github_repo`
source per public repo of the made-up account `test-student`, from saved answers
only (the fake GitHub; tests never reach the live API)."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.github import get_github_client
from app.config import get_settings
from app.db.models import Profile, Source
from app.main import app
from tests.api.test_profile import error_code, log_in, sign_up
from tests.fixtures.github.fake_github import FakeGitHub

LISTING = "/users/test-student/repos?per_page=20&sort=pushed&type=owner"


@pytest.fixture
def fake_github(tmp_path: Path) -> Iterator[FakeGitHub]:
    fake = FakeGitHub()
    # cache_seconds=0: every import asks the fake again, so tests can change answers.
    app.dependency_overrides[get_github_client] = lambda: fake.client(
        tmp_path / "cache", cache_seconds=0
    )
    # The saved repo list is for 20 repos per page, whatever the default or .env says.
    settings = get_settings().model_copy(update={"github_max_repos": 20})
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        yield fake
    finally:
        app.dependency_overrides.pop(get_github_client, None)
        app.dependency_overrides.pop(get_settings, None)


@pytest.fixture
def student(client: TestClient, fake_github: FakeGitHub) -> TestClient:
    sign_up(client, "gh-owner@example.com")
    give_consent(client)
    return client


def give_consent(client: TestClient) -> None:
    """The import refuses without consent (M3.9; tested in test_github_consent.py)."""
    assert client.put("/profile/github-consent").status_code == 200


def import_github(client: TestClient, username: str = "test-student"):  # type: ignore[no-untyped-def]
    return client.post("/sources/github", json={"username": username})


def repo_sources(session: Session) -> list[Source]:
    query = select(Source).where(Source.kind == "github_repo").order_by(Source.title)
    return list(session.scalars(query))


def test_import_stores_one_source_per_repo(student: TestClient, db_session: Session) -> None:
    response = import_github(student)

    assert response.status_code == 200, response.text
    assert [source["title"] for source in response.json()] == [
        "test-student/shop-api",
        "test-student/projet-bibliotheque",
        "test-student/awesome-dashboard",
        "test-student/empty-repo",
    ]
    assert len(repo_sources(db_session)) == 4


def test_repo_source_holds_readme_languages_dependencies_and_commits(
    student: TestClient, db_session: Session
) -> None:
    import_github(student)
    shop = next(s for s in repo_sources(db_session) if s.title == "test-student/shop-api")

    assert shop.text is not None and "FastAPI and PostgreSQL" in shop.text
    assert shop.language == "en"
    assert shop.storage_path is None
    details = shop.details
    assert details["owner"] == "test-student"
    assert details["is_fork"] is False
    assert details["language_shares"] == {"Python": 90.0, "Shell": 6.0, "Dockerfile": 4.0}
    assert details["topics"] == ["fastapi", "postgresql"]
    assert details["commits"] == {"by_user": 42, "total": 50}
    assert [file["path"] for file in details["dependency_files"]] == [
        "requirements.txt",
        "admin/package.json",
    ]


def test_readme_language_is_the_source_language(student: TestClient, db_session: Session) -> None:
    import_github(student)
    languages = {source.title: source.language for source in repo_sources(db_session)}

    assert languages["test-student/projet-bibliotheque"] == "fr"
    assert languages["test-student/empty-repo"] == "other"  # no README: code only
    assert languages["test-student/awesome-dashboard"] == "other"  # fork: README not read


def test_username_is_saved_on_the_profile(student: TestClient, db_session: Session) -> None:
    import_github(student)

    profile = db_session.scalars(select(Profile)).one()
    assert profile.github_username == "test-student"


def test_importing_again_updates_the_same_rows(
    student: TestClient, db_session: Session, fake_github: FakeGitHub
) -> None:
    import_github(student)
    ids_before = {source.title: source.id for source in repo_sources(db_session)}
    # The empty repo was deleted on GitHub since the first import.
    listing = fake_github.responses[LISTING]
    listing["body"] = [repo for repo in listing["body"] if repo["name"] != "empty-repo"]
    listing["headers"] = {}

    response = import_github(student)

    assert response.status_code == 200
    db_session.expire_all()
    ids_after = {source.title: source.id for source in repo_sources(db_session)}
    assert "test-student/empty-repo" not in ids_after
    assert ids_after == {title: ids_before[title] for title in ids_after}


def test_another_username_replaces_the_old_repos(
    student: TestClient, db_session: Session, fake_github: FakeGitHub
) -> None:
    import_github(student)
    fake_github.responses["/users/other-student/repos?per_page=20&sort=pushed&type=owner"] = {
        "status": 200,
        "headers": {},
        "body": [],
    }

    response = import_github(student, "other-student")

    assert response.status_code == 200
    assert response.json() == []
    db_session.expire_all()
    assert repo_sources(db_session) == []


def test_unknown_github_user(student: TestClient, db_session: Session) -> None:
    response = import_github(student, "nobody-here")

    assert response.status_code == 404
    assert error_code(response) == "github_user_not_found"
    assert repo_sources(db_session) == []


def test_rate_limit_answers_429_with_the_reset_time_and_saves_nothing(
    student: TestClient, db_session: Session, fake_github: FakeGitHub
) -> None:
    fake_github.override(
        "/repos/test-student/projet-bibliotheque/languages",
        403,
        {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1795683398"},
    )

    response = import_github(student)

    assert response.status_code == 429
    assert response.json()["detail"] == {
        "code": "github_rate_limited",
        "reset_at": "2026-11-26T08:56:38+00:00",  # the x-ratelimit-reset above
    }
    assert repo_sources(db_session) == []  # shop-api was already read, but not saved


def test_github_down_answers_502(
    student: TestClient, db_session: Session, fake_github: FakeGitHub
) -> None:
    fake_github.override(LISTING, 503)

    response = import_github(student)

    assert response.status_code == 502
    assert error_code(response) == "github_unavailable"


@pytest.mark.parametrize(
    "username",
    ["", "-starts-with-hyphen", "ends-with-hyphen-", "two--hyphens", "has space", "a" * 40, "../x"],
)
def test_invalid_usernames_are_refused_before_asking_github(
    student: TestClient, fake_github: FakeGitHub, username: str
) -> None:
    response = import_github(student, username)

    assert response.status_code == 422
    assert fake_github.requests == []


def test_import_needs_a_login(client: TestClient, fake_github: FakeGitHub) -> None:
    response = import_github(client)

    assert response.status_code == 401
    assert fake_github.requests == []


def test_each_user_has_their_own_repo_sources(
    client: TestClient, db_session: Session, fake_github: FakeGitHub
) -> None:
    sign_up(client, "first-gh@example.com")
    give_consent(client)
    import_github(client)
    sign_up(client, "second-gh@example.com")
    log_in(client, "second-gh@example.com")
    give_consent(client)
    import_github(client)

    sources = repo_sources(db_session)

    assert len(sources) == 8
    assert len({source.user_id for source in sources}) == 2
