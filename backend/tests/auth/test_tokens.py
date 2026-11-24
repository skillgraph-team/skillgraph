"""Tests for app/auth/tokens.py: signed login tokens that name a user and expire."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.auth.tokens import ExpiredTokenError, InvalidTokenError, create_token, read_token

SECRET = "a-test-secret-that-is-long-enough-1234567890"


def test_token_round_trip() -> None:
    user_id = uuid.uuid4()

    assert read_token(create_token(user_id, secret=SECRET), secret=SECRET) == user_id


def test_expired_token_is_rejected() -> None:
    long_ago = datetime.now(UTC) - timedelta(days=30)
    token = create_token(uuid.uuid4(), secret=SECRET, now=long_ago, lifetime=timedelta(hours=1))

    with pytest.raises(ExpiredTokenError):
        read_token(token, secret=SECRET)


def test_token_signed_with_another_secret_is_rejected() -> None:
    token = create_token(uuid.uuid4(), secret="another-secret-that-is-also-long-enough-123")

    with pytest.raises(InvalidTokenError):
        read_token(token, secret=SECRET)


def test_tampered_or_garbage_token_is_rejected() -> None:
    token = create_token(uuid.uuid4(), secret=SECRET)
    tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")

    with pytest.raises(InvalidTokenError):
        read_token(tampered, secret=SECRET)
    with pytest.raises(InvalidTokenError):
        read_token("not-a-token", secret=SECRET)


def test_expired_is_a_kind_of_invalid() -> None:
    """Callers that don't care why can catch InvalidTokenError only."""
    assert issubclass(ExpiredTokenError, InvalidTokenError)
