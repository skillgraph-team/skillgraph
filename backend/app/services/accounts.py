"""Accounts: create a user, and check an email + password at login.

Emails arrive already normalised (trimmed, lowercase) from the API schemas; the
database also refuses uppercase emails (T-057).
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password, verify_dummy, verify_password
from app.db.models import User
from app.db.values import Language


class EmailTakenError(Exception):
    """An account with this email already exists."""


class InvalidCredentialsError(Exception):
    """Unknown email or wrong password (deliberately not saying which)."""


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
