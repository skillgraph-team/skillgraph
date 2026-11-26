"""Tests for deleting an account (M3.9): `POST /account/delete` with the password removes
every row and every file we hold about the user, and nothing of anyone else's.

The user is given data everywhere first: a profile with entries, an uploaded CV (a
file on disk), imported GitHub repos (cached answers on disk), evidence, a skill, a
match and an agent run.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.github import get_github_client
from app.config import get_settings
from app.db.models import Source, User
from app.main import app
from tests.api.test_profile import ENTRIES, PASSWORD, error_code, log_in, sign_up
from tests.db import factories as f
from tests.db.test_delete_user import USER_TABLES
from tests.fixtures.github.fake_github import FakeGitHub

CV = Path(__file__).resolve().parents[1] / "fixtures" / "cv" / "cv_en.pdf"


@pytest.fixture
def folders(tmp_path: Path) -> Iterator[dict[str, Path]]:
    paths = {"uploads": tmp_path / "uploads", "cache": tmp_path / "github_cache"}
    settings = get_settings().model_copy(
        update={
            "upload_dir": paths["uploads"],
            "github_cache_dir": paths["cache"],
            "github_max_repos": 20,
        }
    )
    fake = FakeGitHub()
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_github_client] = lambda: fake.client(paths["cache"])
    try:
        yield paths
    finally:
        app.dependency_overrides.pop(get_settings, None)
        app.dependency_overrides.pop(get_github_client, None)


def fill_account(client: TestClient, session: Session, email: str) -> User:
    """Sign up and give the user data in every table and both file folders."""
    sign_up(client, email)
    for kind, (body, _) in ENTRIES.items():
        assert client.post(f"/profile/{kind}", json=body).status_code == 201
    upload = client.post(
        "/sources/cv", files={"file": ("cv.pdf", CV.read_bytes(), "application/pdf")}
    )
    assert upload.status_code == 201, upload.text
    assert client.put("/profile/github-consent").status_code == 200
    assert client.post("/sources/github", json={"username": "test-student"}).status_code == 200

    user = session.scalars(select(User).where(User.email == email)).one()
    cv = session.scalars(select(Source).where(Source.user_id == user.id, Source.kind == "cv")).one()
    skill = f.make_skill(session)
    evidence = f.make_evidence(session, user, cv)
    f.make_link(session, f.make_user_skill(session, user, skill), evidence)
    f.make_match(session, user, f.make_opportunity(session))
    f.make_message(session, f.make_run(session, user))
    return user


def upload_cv(client: TestClient):  # type: ignore[no-untyped-def]
    return client.post(
        "/sources/cv", files={"file": ("cv.pdf", CV.read_bytes(), "application/pdf")}
    )


def rows_of(session: Session, user_id: object) -> dict[str, int]:
    counts = {}
    for model in USER_TABLES:
        column = model.id if model is User else getattr(model, "user_id", None)  # type: ignore[attr-defined]
        if column is None:
            continue  # tables reached only through a parent (checked by the cascade test)
        counts[model.__tablename__] = session.scalar(
            select(func.count()).select_from(model).where(column == user_id)
        )
    return counts


def total(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def files_in(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*") if p.is_file()) if folder.exists() else []


def delete_account(client: TestClient, password: str = PASSWORD):  # type: ignore[no-untyped-def]
    return client.post("/account/delete", json={"password": password})


def test_deleting_the_account_leaves_no_rows_and_no_files(
    client: TestClient, db_session: Session, folders: dict[str, Path]
) -> None:
    user = fill_account(client, db_session, "leaving@example.com")
    user_id = user.id
    assert all(rows_of(db_session, user_id).values())  # data everywhere before
    assert (folders["uploads"] / str(user_id)).is_dir()
    assert files_in(folders["cache"])

    response = delete_account(client)

    assert response.status_code == 204, response.text
    db_session.expunge_all()
    # This user is the only one, so every personal table must now be empty, including
    # the ones without a user_id column (education, agent messages, ...).
    assert {model.__tablename__: total(db_session, model) for model in USER_TABLES} == {
        model.__tablename__: 0 for model in USER_TABLES
    }
    assert not (folders["uploads"] / str(user_id)).exists()
    assert files_in(folders["cache"]) == []  # the cached GitHub answers for their username


def test_other_users_keep_their_rows_and_files(
    client: TestClient, db_session: Session, folders: dict[str, Path]
) -> None:
    stays = fill_account(client, db_session, "stays@example.com")
    stays_id = stays.id
    stays_rows = rows_of(db_session, stays_id)
    stays_cv = files_in(folders["uploads"] / str(stays_id))
    client.cookies.clear()
    sign_up(client, "goes@example.com")
    upload = client.post(
        "/sources/cv", files={"file": ("cv.pdf", CV.read_bytes(), "application/pdf")}
    )
    assert upload.status_code == 201

    assert delete_account(client).status_code == 204

    db_session.expunge_all()
    assert rows_of(db_session, stays_id) == stays_rows
    assert files_in(folders["uploads"] / str(stays_id)) == stays_cv
    log_in(client, "stays@example.com")
    assert client.get("/auth/me").status_code == 200


def test_deleting_logs_out_and_the_old_login_no_longer_works(
    client: TestClient, folders: dict[str, Path]
) -> None:
    sign_up(client, "bye@example.com")
    login_cookie = dict(client.cookies)

    response = delete_account(client)

    assert response.status_code == 204
    assert "skillgraph_login=" in response.headers["set-cookie"]  # cookie removed
    client.cookies.update(login_cookie)
    assert error_code(client.get("/auth/me")) == "token_invalid"


def test_wrong_password_deletes_nothing(
    client: TestClient, db_session: Session, folders: dict[str, Path]
) -> None:
    user = fill_account(client, db_session, "careful@example.com")
    before = rows_of(db_session, user.id)
    files_before = files_in(folders["uploads"]) + files_in(folders["cache"])

    response = delete_account(client, "not the password")

    assert response.status_code == 403
    assert error_code(response) == "wrong_password"
    assert rows_of(db_session, user.id) == before
    assert files_in(folders["uploads"]) + files_in(folders["cache"]) == files_before


def test_account_without_any_files_can_be_deleted(
    client: TestClient, folders: dict[str, Path]
) -> None:
    sign_up(client, "empty@example.com")

    assert delete_account(client).status_code == 204


def test_deleting_needs_a_login(client: TestClient, folders: dict[str, Path]) -> None:
    response = delete_account(client)

    assert response.status_code == 401
