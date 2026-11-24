"""Tests for app/auth/passwords.py: passwords are stored as argon2 hashes, never as text."""

from app.auth.passwords import hash_password, verify_password


def test_hash_is_not_the_password_and_is_argon2() -> None:
    hashed = hash_password("correct horse battery")

    assert "correct horse battery" not in hashed
    assert hashed.startswith("$argon2id$")


def test_same_password_gives_different_hashes() -> None:
    assert hash_password("same password!") != hash_password("same password!")


def test_verify_accepts_right_and_rejects_wrong_password() -> None:
    hashed = hash_password("correct horse battery")

    assert verify_password("correct horse battery", hashed)
    assert not verify_password("wrong horse battery", hashed)
