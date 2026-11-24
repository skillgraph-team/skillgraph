"""The login cookie (D-015): the token travels in a cookie the browser's scripts can't read.

- HttpOnly: JavaScript can't read it, so an injected script can't steal the login.
- SameSite=Lax: the browser doesn't send it with requests that other sites start
  (forms, fetch), which blocks cross-site request forgery for our POST/PUT/DELETE.
- Secure (production, COOKIE_SECURE=true): only sent over HTTPS.
"""

from fastapi import Response

from app.config import get_settings

COOKIE_NAME = "skillgraph_login"


def set_login_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.login_lifetime_hours * 3600,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )


def clear_login_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        COOKIE_NAME, httponly=True, samesite="lax", secure=settings.cookie_secure, path="/"
    )
