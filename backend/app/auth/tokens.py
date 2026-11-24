"""Signed login tokens (JWT, HS256, via PyJWT): who is logged in, and until when.

A token holds the user id (`sub`), when it was made (`iat`) and when it expires (`exp`).
It is signed with SECRET_KEY, so it can't be forged or edited without the key. There
is no server-side list of tokens: logging out deletes the cookie, and a stolen token
stays valid until it expires (see D-015).
"""

import uuid
from datetime import UTC, datetime, timedelta

import jwt

_ALGORITHM = "HS256"


class InvalidTokenError(Exception):
    """The token is malformed, forged, or signed with another key."""


class ExpiredTokenError(InvalidTokenError):
    """The token was valid but its time is up: the user must log in again."""


def create_token(
    user_id: uuid.UUID,
    *,
    secret: str,
    lifetime: timedelta = timedelta(hours=24),
    now: datetime | None = None,
) -> str:
    issued = now or datetime.now(UTC)
    claims = {"sub": str(user_id), "iat": issued, "exp": issued + lifetime}
    return jwt.encode(claims, secret, algorithm=_ALGORITHM)


def read_token(token: str, *, secret: str) -> uuid.UUID:
    """The user id in a valid token. Raises ExpiredTokenError or InvalidTokenError."""
    try:
        claims = jwt.decode(
            token, secret, algorithms=[_ALGORITHM], options={"require": ["sub", "exp", "iat"]}
        )
        return uuid.UUID(claims["sub"])
    except jwt.ExpiredSignatureError as error:
        raise ExpiredTokenError from error
    except (jwt.InvalidTokenError, ValueError) as error:
        raise InvalidTokenError from error
