"""Tests for app/api/auth.py: sign up, log in, log out, and the "current user" check.

The login token travels in an HttpOnly cookie (D-015). The test client keeps cookies
between requests like a browser does. Errors come back as codes: {"detail": {"code": ...}}.
"""

import uuid
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth.cookies import COOKIE_NAME
from app.auth.tokens import create_token
from app.config import get_settings
from app.db.models import User

PASSWORD = "a long enough password"


def sign_up(client: TestClient, email: str = "student@example.com", **extra: str) -> dict:  # type: ignore[type-arg]
    response = client.post("/auth/signup", json={"email": email, "password": PASSWORD} | extra)
    assert response.status_code == 201, response.text
    return response.json()  # type: ignore[no-any-return]


def error_code(response) -> str:  # type: ignore[no-untyped-def]
    return response.json()["detail"]["code"]  # type: ignore[no-any-return]


# --- sign up -----------------------------------------------------------------


def test_sign_up_creates_the_user_and_logs_them_in(client: TestClient) -> None:
    body = sign_up(client, email="New.Student@Example.com", preferred_language="ar")

    assert body["email"] == "new.student@example.com"
    assert body["preferred_language"] == "ar"
    assert "password" not in str(body)
    assert client.get("/auth/me").json()["id"] == body["id"]


def test_sign_up_cookie_is_http_only_and_same_site(client: TestClient) -> None:
    response = client.post(
        "/auth/signup", json={"email": "cookie@example.com", "password": PASSWORD}
    )

    cookie = response.headers["set-cookie"].lower()
    assert f"{COOKIE_NAME}=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_sign_up_stores_a_hash_not_the_password(client: TestClient, db_session: Session) -> None:
    body = sign_up(client)

    user = db_session.get(User, uuid.UUID(body["id"]))
    assert user is not None
    assert PASSWORD not in user.password_hash


def test_sign_up_twice_with_the_same_email_is_refused(client: TestClient) -> None:
    sign_up(client, email="twice@example.com")

    response = client.post(
        "/auth/signup", json={"email": "TWICE@example.com", "password": PASSWORD}
    )

    assert response.status_code == 409
    assert error_code(response) == "email_taken"


def test_sign_up_refuses_short_password_and_bad_email(client: TestClient) -> None:
    short = client.post("/auth/signup", json={"email": "a@example.com", "password": "short"})
    bad_email = client.post("/auth/signup", json={"email": "not-an-email", "password": PASSWORD})
    bad_language = client.post(
        "/auth/signup",
        json={"email": "b@example.com", "password": PASSWORD, "preferred_language": "de"},
    )

    assert short.status_code == 422
    assert bad_email.status_code == 422
    assert bad_language.status_code == 422


# --- log in ------------------------------------------------------------------


def test_log_in_with_the_right_password(client: TestClient) -> None:
    created = sign_up(client, email="login@example.com")
    client.cookies.clear()

    response = client.post("/auth/login", json={"email": "Login@example.com", "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert client.get("/auth/me").status_code == 200


def test_log_in_with_the_wrong_password_is_refused(client: TestClient) -> None:
    sign_up(client, email="wrong@example.com")
    client.cookies.clear()

    response = client.post(
        "/auth/login", json={"email": "wrong@example.com", "password": "not the password"}
    )

    assert response.status_code == 401
    assert error_code(response) == "invalid_credentials"
    assert COOKIE_NAME not in client.cookies


def test_unknown_email_gets_the_same_answer_as_a_wrong_password(client: TestClient) -> None:
    """So nobody can find out which emails have an account."""
    response = client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )

    assert response.status_code == 401
    assert error_code(response) == "invalid_credentials"


# --- the current-user check --------------------------------------------------


def test_protected_endpoint_rejects_anonymous_requests(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert error_code(response) == "not_authenticated"


def test_protected_endpoint_rejects_an_expired_token(client: TestClient) -> None:
    body = sign_up(client)
    expired = create_token(
        uuid.UUID(body["id"]),
        secret=get_settings().secret_key,
        now=datetime.now(UTC) - timedelta(days=30),
        lifetime=timedelta(hours=1),
    )
    client.cookies.set(COOKIE_NAME, expired)

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert error_code(response) == "token_expired"


def test_protected_endpoint_rejects_a_forged_token(client: TestClient) -> None:
    client.cookies.set(COOKIE_NAME, "forged.token.value")

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert error_code(response) == "token_invalid"


def test_token_of_a_deleted_user_is_rejected(client: TestClient, db_session: Session) -> None:
    body = sign_up(client)
    db_session.execute(delete(User).where(User.id == uuid.UUID(body["id"])))

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert error_code(response) == "token_invalid"


# --- log out -----------------------------------------------------------------


def test_log_out_removes_the_cookie(client: TestClient) -> None:
    sign_up(client)

    response = client.post("/auth/logout")

    assert response.status_code == 204
    assert COOKIE_NAME not in client.cookies
    assert client.get("/auth/me").status_code == 401
