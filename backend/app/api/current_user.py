"""The "current user" check for protected endpoints.

Add a parameter `user: CurrentUser` to an endpoint and it only runs for a logged-in
caller; anyone else gets 401 with one of these codes:
- `not_authenticated`: no login cookie
- `token_expired`: the login is too old; log in again
- `token_invalid`: forged or broken token, or the account no longer exists
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from sqlalchemy import select

from app.auth.cookies import COOKIE_NAME
from app.auth.tokens import ExpiredTokenError, InvalidTokenError, read_token
from app.config import get_settings
from app.db.models import User
from app.db.session import DbSession

# auto_error=False: we answer with our own error codes. Also documents the cookie in /docs.
_login_cookie = APIKeyCookie(name=COOKIE_NAME, auto_error=False)


def _unauthorized(code: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail={"code": code})


def get_current_user(
    session: DbSession, token: Annotated[str | None, Depends(_login_cookie)]
) -> User:
    if not token:
        raise _unauthorized("not_authenticated")
    try:
        user_id = read_token(token, secret=get_settings().secret_key)
    except ExpiredTokenError:
        raise _unauthorized("token_expired") from None
    except InvalidTokenError:
        raise _unauthorized("token_invalid") from None
    # A query, not session.get(): always asks the database, so a deleted user is caught.
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise _unauthorized("token_invalid")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
