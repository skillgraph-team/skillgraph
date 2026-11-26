"""Accounts: create a user, check an email + password at login, delete an account.

Emails arrive already normalised (trimmed, lowercase) from the API schemas; the
database also refuses uppercase emails (T-057).

Deleting an account (M3.9) removes the files first, then the rows:
1. the user's upload folder `<upload_dir>/<user id>/` (their CVs, T-086);
2. the cached GitHub answers for their GitHub username (T-093);
3. the `users` row; the database deletes every other personal row with it
   (ON DELETE CASCADE, see docs/design/schema.md and tests/db/test_delete_user.py).
Files first: if removing them fails, the error stops everything before any row is
deleted, so the user still has an account and can try again. The other way round, a
failure would leave their CV on disk with no account left to delete it from.
"""

import shutil
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password, verify_dummy, verify_password
from app.db.models import Profile, User
from app.db.values import Language
from app.ingestion.github_client import forget_cached_user


class EmailTakenError(Exception):
    """An account with this email already exists."""


class InvalidCredentialsError(Exception):
    """Unknown email or wrong password (deliberately not saying which)."""


class WrongPasswordError(Exception):
    """The logged-in user typed a password that isn't theirs (checked before deleting)."""


def sign_up(session: Session, *, email: str, password: str, language: Language) -> User:
    user = User(email=email, password_hash=hash_password(password), preferred_language=language)
    try:
        # A savepoint, so a duplicate email only undoes this insert.
        with session.begin_nested():
            session.add(user)
    except IntegrityError as error:
        raise EmailTakenError from error
    return user


def log_in(session: Session, *, email: str, password: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        verify_dummy(password)
        raise InvalidCredentialsError
    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError
    return user


def delete_account(
    session: Session, user: User, *, password: str, upload_dir: Path, github_cache_dir: Path
) -> None:
    if not verify_password(password, user.password_hash):
        raise WrongPasswordError

    user_folder = upload_dir / str(user.id)  # the id is a UUID: it can't point elsewhere
    if user_folder.exists():
        shutil.rmtree(user_folder)
    username = session.scalar(select(Profile.github_username).where(Profile.user_id == user.id))
    if username:
        forget_cached_user(github_cache_dir, username)

    session.delete(user)
    session.flush()
