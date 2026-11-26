"""Tests for changing the password (M3.10): `POST /auth/password`
{current_password, new_password} → 204, and the user stays logged in.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from tests.api.test_profile import PASSWORD, error_code, sign_up

EMAIL = "change@example.com"
NEW_PASSWORD = "a brand new long password"


def change(client: TestClient, current: str, new: str):  # type: ignore[no-untyped-def]
    return client.post("/auth/password", json={"current_password": current, "new_password": new})


def login(client: TestClient, password: str) -> int:
    client.cookies.clear()
    return client.post("/auth/login", json={"email": EMAIL, "password": password}).status_code


def test_the_new_password_works_and_the_old_one_does_not(client: TestClient) -> None:
    sign_up(client, EMAIL)

    response = change(client, PASSWORD, NEW_PASSWORD)

    assert response.status_code == 204
    assert login(client, NEW_PASSWORD) == 200
    assert login(client, PASSWORD) == 401


def test_the_user_stays_logged_in(client: TestClient) -> None:
    sign_up(client, EMAIL)

    change(client, PASSWORD, NEW_PASSWORD)

    assert client.get("/auth/me").status_code == 200


def test_a_wrong_current_password_changes_nothing(client: TestClient, db_session: Session) -> None:
    sign_up(client, EMAIL)
    before = db_session.scalar(select(User.password_hash).where(User.email == EMAIL))

    response = change(client, "not my password", NEW_PASSWORD)

    assert response.status_code == 401
    assert error_code(response) == "invalid_credentials"
    db_session.expire_all()
    assert db_session.scalar(select(User.password_hash).where(User.email == EMAIL)) == before
    assert client.get("/auth/me").status_code == 200  # still logged in
    assert login(client, PASSWORD) == 200
    assert login(client, NEW_PASSWORD) == 401


def test_the_new_password_follows_the_sign_up_rules(client: TestClient) -> None:
    sign_up(client, EMAIL)

    assert change(client, PASSWORD, "short").status_code == 422
    assert change(client, PASSWORD, "x" * 129).status_code == 422
    assert login(client, PASSWORD) == 200


def test_unknown_fields_are_refused(client: TestClient) -> None:
    sign_up(client, EMAIL)

    body = {"current_password": PASSWORD, "new_password": NEW_PASSWORD, "email": "x@y.z"}
    assert client.post("/auth/password", json=body).status_code == 422


def test_changing_the_password_needs_a_login(client: TestClient) -> None:
    response = change(client, PASSWORD, NEW_PASSWORD)

    assert response.status_code == 401
    assert error_code(response) == "not_authenticated"
