"""Tests for the skills endpoints (M4.5): POST /skills/build, GET /skills and
PATCH /skills/{id}. Needs the test database. The CV is a made-up fixture file."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.skills.taxonomy import load_taxonomy
from tests.api.test_profile import error_code, log_in, sign_up

CV = Path(__file__).resolve().parents[1] / "fixtures" / "cv" / "cv_en.pdf"


@pytest.fixture
def student(client: TestClient, db_session: Session) -> TestClient:
    load_taxonomy(db_session)
    sign_up(client, "owner@example.com")
    with CV.open("rb") as f:
        response = client.post("/sources/cv", files={"file": ("cv.pdf", f, "application/pdf")})
    assert response.status_code == 201, response.text
    return client


def skill(skills: list[dict], skill_id: str) -> dict:  # type: ignore[type-arg]
    return next(s for s in skills if s["skill_id"] == skill_id)


def test_build_returns_the_skills_with_status_reason_and_evidence(student: TestClient) -> None:
    response = student.post("/skills/build")
    assert response.status_code == 200, response.text
    python = skill(response.json(), "python")
    assert python["names"] == {"en": "Python", "fr": "Python", "ar": "Python"}
    assert (python["status"], python["confidence"]) == ("claimed", "medium")
    assert python["reason"]["code"] == "named_in_list"
    [evidence] = python["evidence"]
    assert evidence["type"] == "cv_skills_list"
    assert evidence["quote"] == "Skills: Python, FastAPI, PostgreSQL and Docker."
    assert evidence["judgement"] == "supports"
    assert evidence["language"] == "en"
    assert evidence["id"] == python["reason"]["evidence_id"]
    assert (python["hidden"], python["disputed"], python["note"]) == (False, False, None)


def test_get_lists_the_same_skills_strongest_first(student: TestClient) -> None:
    built = student.post("/skills/build").json()
    listed = student.get("/skills").json()
    assert listed == built
    order = {"assessed": 3, "demonstrated": 2, "claimed": 1, "unverified": 0}
    ranks = [order[s["status"]] for s in listed]
    assert ranks == sorted(ranks, reverse=True)
    assert {s["skill_id"] for s in listed} >= {"python", "django", "pytest", "rest-api"}


def test_a_new_user_has_no_skills(client: TestClient) -> None:
    sign_up(client, "new@example.com")
    assert client.get("/skills").json() == []


def test_hide_dispute_and_note(student: TestClient) -> None:
    python = skill(student.post("/skills/build").json(), "python")

    response = student.patch(
        f"/skills/{python['id']}", json={"hidden": True, "disputed": True, "note": "Only a course"}
    )

    assert response.status_code == 200, response.text
    changed = response.json()
    assert (changed["hidden"], changed["disputed"], changed["note"]) == (
        True,
        True,
        "Only a course",
    )
    assert (changed["status"], changed["confidence"]) == (python["status"], python["confidence"])

    rebuilt = skill(student.post("/skills/build").json(), "python")
    assert (rebuilt["hidden"], rebuilt["disputed"], rebuilt["note"]) == (
        True,
        True,
        "Only a course",
    )

    cleared = student.patch(f"/skills/{python['id']}", json={"hidden": False, "note": None})
    assert (cleared.json()["hidden"], cleared.json()["note"]) == (False, None)
    assert cleared.json()["disputed"] is True


def test_status_and_confidence_cant_be_changed(student: TestClient) -> None:
    python = skill(student.post("/skills/build").json(), "python")
    response = student.patch(f"/skills/{python['id']}", json={"status": "assessed"})
    assert response.status_code == 422


def test_a_note_is_at_most_500_characters(student: TestClient) -> None:
    python = skill(student.post("/skills/build").json(), "python")
    response = student.patch(f"/skills/{python['id']}", json={"note": "x" * 501})
    assert response.status_code == 422


def test_someone_elses_skill_answers_404(student: TestClient) -> None:
    python = skill(student.post("/skills/build").json(), "python")
    sign_up(student, "other@example.com")

    hide = student.patch(f"/skills/{python['id']}", json={"hidden": True})
    dispute = student.patch(f"/skills/{python['id']}", json={"disputed": True})

    assert (hide.status_code, error_code(hide)) == (404, "not_found")
    assert (dispute.status_code, error_code(dispute)) == (404, "not_found")
    log_in(student, "owner@example.com")
    assert skill(student.get("/skills").json(), "python")["hidden"] is False


def test_an_unknown_id_answers_404(student: TestClient) -> None:
    response = student.patch("/skills/00000000-0000-0000-0000-000000000000", json={"hidden": True})
    assert (response.status_code, error_code(response)) == (404, "not_found")


def test_logged_out_is_refused(client: TestClient) -> None:
    assert client.get("/skills").status_code == 401
    assert client.post("/skills/build").status_code == 401


def test_without_the_skill_list_the_build_answers_503(client: TestClient) -> None:
    sign_up(client, "early@example.com")
    response = client.post("/skills/build")
    assert (response.status_code, error_code(response)) == (503, "skill_list_not_loaded")
