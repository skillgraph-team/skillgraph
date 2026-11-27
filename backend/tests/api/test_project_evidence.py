"""API tests for manual projects as evidence and removing sources (M4.10): the project
endpoints update the skills, and the sources endpoints only show CVs and repos.
Needs the test database. The CV is a made-up fixture file."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Source
from app.skills.taxonomy import load_taxonomy
from tests.api.test_profile import error_code, sign_up

CV = Path(__file__).resolve().parents[1] / "fixtures" / "cv" / "cv_en.pdf"
PROJECT = {"title": "Chat app", "description": "Built a chat app with Flask and Redis."}


@pytest.fixture
def student(client: TestClient, db_session: Session) -> TestClient:
    load_taxonomy(db_session)
    sign_up(client, "owner@example.com")
    return client


def skill_ids(client: TestClient) -> set[str]:
    return {s["skill_id"] for s in client.get("/skills").json()}


def test_adding_editing_and_deleting_a_project_updates_the_skills(student: TestClient) -> None:
    project = student.post("/profile/projects", json=PROJECT).json()
    assert skill_ids(student) == {"flask", "redis"}

    student.put(
        f"/profile/projects/{project['id']}",
        json=PROJECT | {"description": "Built a chat app with Django."},
    )
    assert skill_ids(student) == {"django"}

    assert student.delete(f"/profile/projects/{project['id']}").status_code == 204
    assert skill_ids(student) == set()


def test_deleting_the_cv_removes_its_skills(student: TestClient) -> None:
    with CV.open("rb") as f:
        cv = student.post("/sources/cv", files={"file": ("cv.pdf", f, "application/pdf")}).json()
    student.post("/skills/build")
    student.post("/profile/projects", json=PROJECT)
    assert {"python", "flask"} <= skill_ids(student)

    assert student.delete(f"/sources/{cv['id']}").status_code == 204

    assert skill_ids(student) == {"flask", "redis"}


def test_project_sources_are_not_listed_or_deletable_as_sources(
    student: TestClient, db_session: Session
) -> None:
    student.post("/profile/projects", json=PROJECT)
    source = db_session.scalar(select(Source).where(Source.kind == "manual_project"))
    assert source is not None

    assert student.get("/sources").json() == []
    response = student.delete(f"/sources/{source.id}")
    assert (response.status_code, error_code(response)) == (404, "not_found")
