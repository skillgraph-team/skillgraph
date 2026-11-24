"""Tests for the profile API (M3.3): the profile itself, the preferred language, and the
education / experience / project lists.

The ownership rule matters most: another user's entries answer 404 `not_found`, as if
they didn't exist, for reading, changing and deleting.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

PASSWORD = "a long enough password"

# One valid body per list, and the field we change in the update tests.
ENTRIES: dict[str, tuple[dict[str, Any], str]] = {
    "education": (
        {
            "institution": "Example University",
            "degree": "BSc",
            "field_of_study": "Computer Science",
            "start_date": "2022-09-01",
            "end_date": "2025-06-30",
            "description": "Databases, algorithms.",
        },
        "institution",
    ),
    "experience": (
        {
            "organization": "Example Startup",
            "role": "Backend intern",
            "start_date": "2024-06-01",
            "end_date": None,
            "description": "Wrote REST endpoints in FastAPI.",
        },
        "organization",
    ),
    "projects": (
        {
            "title": "Library app",
            "description": "A library management app with Django and PostgreSQL.",
            "url": "https://example.com/library-app",
        },
        "title",
    ),
}
KINDS = list(ENTRIES)


def sign_up(client: TestClient, email: str, **extra: str) -> None:
    response = client.post("/auth/signup", json={"email": email, "password": PASSWORD} | extra)
    assert response.status_code == 201, response.text


def log_in(client: TestClient, email: str) -> None:
    client.cookies.clear()
    response = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text


def error_code(response) -> str:  # type: ignore[no-untyped-def]
    return response.json()["detail"]["code"]  # type: ignore[no-any-return]


@pytest.fixture
def student(client: TestClient) -> TestClient:
    sign_up(client, "owner@example.com")
    return client


# --- the profile -------------------------------------------------------------


def test_new_user_gets_an_empty_profile(student: TestClient) -> None:
    response = student.get("/profile")

    assert response.status_code == 200
    assert response.json() == {
        "display_name": None,
        "headline": None,
        "preferred_language": "en",
        "education": [],
        "experience": [],
        "projects": [],
    }


def test_update_the_profile(student: TestClient) -> None:
    response = student.patch(
        "/profile", json={"display_name": "Test Student", "headline": "CS student"}
    )

    assert response.status_code == 200
    body = student.get("/profile").json()
    assert body["display_name"] == "Test Student"
    assert body["headline"] == "CS student"


def test_patch_changes_only_the_fields_sent(student: TestClient) -> None:
    student.patch("/profile", json={"display_name": "Test Student", "headline": "CS student"})

    student.patch("/profile", json={"headline": None})

    body = student.get("/profile").json()
    assert body["display_name"] == "Test Student"
    assert body["headline"] is None


def test_change_the_preferred_language(student: TestClient) -> None:
    response = student.patch("/profile", json={"preferred_language": "ar"})

    assert response.status_code == 200
    assert response.json()["preferred_language"] == "ar"
    assert student.get("/auth/me").json()["preferred_language"] == "ar"


def test_preferred_language_must_be_one_of_the_three(student: TestClient) -> None:
    assert student.patch("/profile", json={"preferred_language": "de"}).status_code == 422
    assert student.patch("/profile", json={"preferred_language": None}).status_code == 422


def test_profile_refuses_unknown_and_too_long_fields(student: TestClient) -> None:
    assert student.patch("/profile", json={"github_consent_at": "2026-01-01"}).status_code == 422
    assert student.patch("/profile", json={"display_name": "x" * 201}).status_code == 422


def test_delete_the_profile_removes_its_entries_but_keeps_the_account(
    student: TestClient,
) -> None:
    student.patch("/profile", json={"display_name": "Test Student", "preferred_language": "fr"})
    for kind in KINDS:
        student.post(f"/profile/{kind}", json=ENTRIES[kind][0])

    response = student.delete("/profile")

    assert response.status_code == 204
    assert student.get("/profile").json() == {
        "display_name": None,
        "headline": None,
        "preferred_language": "fr",  # a setting of the account, not profile content
        "education": [],
        "experience": [],
        "projects": [],
    }
    assert student.get("/auth/me").status_code == 200


def test_profile_endpoints_need_a_login(client: TestClient) -> None:
    calls = [
        client.get("/profile"),
        client.patch("/profile", json={}),
        client.delete("/profile"),
    ]
    for kind in KINDS:
        calls.append(client.get(f"/profile/{kind}"))
        calls.append(client.post(f"/profile/{kind}", json=ENTRIES[kind][0]))

    for response in calls:
        assert response.status_code == 401
        assert error_code(response) == "not_authenticated"


# --- education, experience, projects: the same four operations each ----------


@pytest.mark.parametrize("kind", KINDS)
def test_create_and_list_entries(student: TestClient, kind: str) -> None:
    body, _ = ENTRIES[kind]

    response = student.post(f"/profile/{kind}", json=body)

    assert response.status_code == 201, response.text
    created = response.json()
    assert {key: created[key] for key in body} == body
    assert "id" in created
    listed = student.get(f"/profile/{kind}").json()
    assert [entry["id"] for entry in listed] == [created["id"]]
    assert student.get("/profile").json()[kind] == listed


@pytest.mark.parametrize("kind", KINDS)
def test_entries_are_listed_in_position_order(student: TestClient, kind: str) -> None:
    body, field = ENTRIES[kind]
    first = student.post(f"/profile/{kind}", json=body | {field: "First"}).json()
    second = student.post(f"/profile/{kind}", json=body | {field: "Second"}).json()
    assert (first["position"], second["position"]) == (0, 1)  # new entries go last

    student.put(f"/profile/{kind}/{first['id']}", json=body | {field: "First", "position": 5})

    listed = student.get(f"/profile/{kind}").json()
    assert [entry[field] for entry in listed] == ["Second", "First"]


@pytest.mark.parametrize("kind", KINDS)
def test_update_an_entry(student: TestClient, kind: str) -> None:
    body, field = ENTRIES[kind]
    created = student.post(f"/profile/{kind}", json=body).json()

    response = student.put(f"/profile/{kind}/{created['id']}", json=body | {field: "Changed"})

    assert response.status_code == 200
    assert response.json()[field] == "Changed"
    assert student.get(f"/profile/{kind}").json()[0][field] == "Changed"


@pytest.mark.parametrize("kind", KINDS)
def test_delete_an_entry(student: TestClient, kind: str) -> None:
    created = student.post(f"/profile/{kind}", json=ENTRIES[kind][0]).json()

    response = student.delete(f"/profile/{kind}/{created['id']}")

    assert response.status_code == 204
    assert student.get(f"/profile/{kind}").json() == []


@pytest.mark.parametrize("kind", KINDS)
def test_unknown_entry_is_not_found(student: TestClient, kind: str) -> None:
    missing = "00000000-0000-0000-0000-000000000000"
    body = ENTRIES[kind][0]

    for response in (
        student.put(f"/profile/{kind}/{missing}", json=body),
        student.delete(f"/profile/{kind}/{missing}"),
    ):
        assert response.status_code == 404
        assert error_code(response) == "not_found"


@pytest.mark.parametrize("kind", KINDS)
def test_required_text_cannot_be_empty(student: TestClient, kind: str) -> None:
    body, field = ENTRIES[kind]

    assert student.post(f"/profile/{kind}", json=body | {field: "   "}).status_code == 422
    assert student.post(f"/profile/{kind}", json=body | {field: None}).status_code == 422
    assert student.post(f"/profile/{kind}", json=body | {"extra": 1}).status_code == 422


@pytest.mark.parametrize("kind", ["education", "experience"])
def test_end_date_cannot_be_before_start_date(student: TestClient, kind: str) -> None:
    body = ENTRIES[kind][0] | {"start_date": "2025-01-01", "end_date": "2024-01-01"}

    assert student.post(f"/profile/{kind}", json=body).status_code == 422


def test_project_url_must_be_a_web_address(student: TestClient) -> None:
    body = ENTRIES["projects"][0]

    for bad in ("javascript:alert(1)", "example.com", "ftp://example.com"):
        assert student.post("/profile/projects", json=body | {"url": bad}).status_code == 422
    assert student.post("/profile/projects", json=body | {"url": None}).status_code == 201


# --- one user can't see or change another user's data --------------------------


@pytest.mark.parametrize("kind", KINDS)
def test_a_user_cannot_read_change_or_delete_another_users_entries(
    client: TestClient, kind: str
) -> None:
    body, field = ENTRIES[kind]
    sign_up(client, "owner@example.com")
    client.patch("/profile", json={"display_name": "Owner"})
    owned = client.post(f"/profile/{kind}", json=body).json()

    sign_up(client, "intruder@example.com")  # the cookie now belongs to the intruder
    assert client.get(f"/profile/{kind}").json() == []
    assert client.get("/profile").json()["display_name"] is None
    changed = client.put(f"/profile/{kind}/{owned['id']}", json=body | {field: "Hacked"})
    deleted = client.delete(f"/profile/{kind}/{owned['id']}")
    for response in (changed, deleted):
        assert response.status_code == 404
        assert error_code(response) == "not_found"
    client.delete("/profile")  # deleting your own profile doesn't touch anyone else's

    log_in(client, "owner@example.com")
    entries = client.get(f"/profile/{kind}").json()
    assert [(entry["id"], entry[field]) for entry in entries] == [(owned["id"], body[field])]
    assert client.get("/profile").json()["display_name"] == "Owner"
