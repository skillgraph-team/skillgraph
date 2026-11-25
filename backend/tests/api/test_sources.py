"""Tests for CV upload (M3.5): `POST /sources/cv` stores the file outside any public
folder, saves its text and language as a `sources` row, and refuses bad files with a
clear code, without storing anything.

Uploaded files go to a temporary folder per test (the `upload_dir` fixture).
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.models import Source
from app.main import app
from tests.api.test_profile import error_code, log_in, sign_up
from tests.fixtures.cv.make_cv_fixtures import CV_LINES

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "cv"
MAX_BYTES = 100_000  # small limit for tests; the fixtures are 20-40 KB

PDF = "application/pdf"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@pytest.fixture
def upload_dir(tmp_path: Path) -> Iterator[Path]:
    folder = tmp_path / "uploads"
    settings = get_settings().model_copy(update={"upload_dir": folder, "cv_max_bytes": MAX_BYTES})
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        yield folder
    finally:
        app.dependency_overrides.pop(get_settings, None)


@pytest.fixture
def student(client: TestClient, upload_dir: Path) -> TestClient:
    sign_up(client, "cv-owner@example.com")
    return client


def upload(client: TestClient, name: str, data: bytes, content_type: str = PDF):  # type: ignore[no-untyped-def]
    return client.post("/sources/cv", files={"file": (name, data, content_type)})


def stored_files(folder: Path) -> list[Path]:
    return [path for path in folder.rglob("*") if path.is_file()] if folder.exists() else []


@pytest.mark.parametrize("language", ["en", "fr", "ar"])
@pytest.mark.parametrize(("extension", "content_type"), [("pdf", PDF), ("docx", DOCX)])
def test_upload_stores_text_and_language(
    student: TestClient,
    db_session: Session,
    upload_dir: Path,
    language: str,
    extension: str,
    content_type: str,
) -> None:
    data = (FIXTURES / f"cv_{language}.{extension}").read_bytes()

    response = upload(student, f"my cv.{extension}", data, content_type)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["kind"] == "cv"
    assert body["title"] == f"my cv.{extension}"
    assert body["language"] == language
    assert body["text"].splitlines() == CV_LINES[language]
    assert body["details"]["file_type"] == extension
    assert body["details"]["size_bytes"] == len(data)

    source = db_session.scalars(select(Source)).one()
    assert str(source.id) == body["id"]
    assert source.text == body["text"]
    assert source.language == language
    assert source.storage_path is not None
    assert (upload_dir / source.storage_path).read_bytes() == data


def test_file_is_stored_under_the_upload_folder_by_id_not_by_name(
    student: TestClient, db_session: Session, upload_dir: Path
) -> None:
    """The name the browser sends is only a label: a name like ../../evil.pdf must not
    decide where the file goes."""
    data = (FIXTURES / "cv_en.pdf").read_bytes()

    response = upload(student, "../../evil.pdf", data)

    assert response.status_code == 201
    assert response.json()["title"] == "evil.pdf"
    source = db_session.scalars(select(Source)).one()
    assert source.storage_path == f"{source.user_id}/{source.id}.pdf"
    assert stored_files(upload_dir) == [upload_dir / str(source.user_id) / f"{source.id}.pdf"]


def test_type_is_read_from_the_file_not_from_its_name(student: TestClient) -> None:
    data = (FIXTURES / "cv_fr.docx").read_bytes()

    response = upload(student, "cv.pdf", data, PDF)

    assert response.status_code == 201
    assert response.json()["details"]["file_type"] == "docx"


@pytest.mark.parametrize(
    ("name", "data", "status", "code"),
    [
        ("notes.txt", b"Python, SQL", 415, "unsupported_file_type"),
        ("photo.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 50, 415, "unsupported_file_type"),
        ("cv.pdf", (FIXTURES / "cv_en.pdf").read_bytes()[:2000], 422, "file_unreadable"),
        ("scan.pdf", (FIXTURES / "cv_scanned.pdf").read_bytes(), 422, "no_text_found"),
        ("big.pdf", b"%PDF-1.7\n" + b"0" * MAX_BYTES, 413, "file_too_large"),
    ],
    ids=["text", "png", "broken-pdf", "scanned", "too-large"],
)
def test_bad_files_get_a_clear_error_and_nothing_is_stored(
    student: TestClient,
    db_session: Session,
    upload_dir: Path,
    name: str,
    data: bytes,
    status: int,
    code: str,
) -> None:
    response = upload(student, name, data)

    assert response.status_code == status, response.text
    assert error_code(response) == code
    assert db_session.scalars(select(Source)).all() == []
    assert stored_files(upload_dir) == []


def test_upload_without_a_file_is_refused(student: TestClient) -> None:
    response = student.post("/sources/cv")

    assert response.status_code == 422


def test_upload_needs_a_login(client: TestClient, upload_dir: Path) -> None:
    response = upload(client, "cv.pdf", (FIXTURES / "cv_en.pdf").read_bytes())

    assert response.status_code == 401
    assert stored_files(upload_dir) == []


def test_each_upload_belongs_to_its_uploader(
    client: TestClient, db_session: Session, upload_dir: Path
) -> None:
    sign_up(client, "first@example.com")
    upload(client, "first.pdf", (FIXTURES / "cv_en.pdf").read_bytes())
    sign_up(client, "second@example.com")
    log_in(client, "second@example.com")
    upload(client, "second.pdf", (FIXTURES / "cv_fr.pdf").read_bytes())

    sources = db_session.scalars(select(Source).order_by(Source.title)).all()

    assert [source.title for source in sources] == ["first.pdf", "second.pdf"]
    assert sources[0].user_id != sources[1].user_id
    for source in sources:
        assert source.storage_path is not None
        assert source.storage_path.startswith(f"{source.user_id}/")


def test_settings_default_upload_folder_is_git_ignored() -> None:
    """The default folder must be backend/storage/, which .gitignore leaves out, and
    must not be inside a folder the web server publishes."""
    default = Settings.model_fields["upload_dir"].default

    assert default.parts[-3:] == ("backend", "storage", "uploads")
