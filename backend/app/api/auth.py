"""Sign up, log in, log out, and "who am I" (M3.1, D-015).

POST /auth/signup  {email, password, preferred_language?} → 201 user, sets the login cookie
POST /auth/login   {email, password}                     → 200 user, sets the login cookie
POST /auth/logout                                        → 204, removes the login cookie
GET  /auth/me                                            → 200 user (needs a login)

Errors: 409 `email_taken`, 401 `invalid_credentials` (same for unknown email and wrong
password), 422 for invalid input (FastAPI's standard validation answer).
"""

import re
import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.api.current_user import CurrentUser
from app.auth.cookies import clear_login_cookie, set_login_cookie
from app.auth.tokens import create_token
from app.config import get_settings
from app.db.models import User
from app.db.session import DbSession
from app.db.values import Language
from app.services.accounts import EmailTakenError, InvalidCredentialsError, log_in, sign_up

router = APIRouter(prefix="/auth", tags=["auth"])

# Deliberately simple: something@something.something. The real check is that the user
# can log in with it; sending email isn't part of the MVP.
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalise_email(value: str) -> str:
    value = value.strip().lower()
    if not _EMAIL.match(value):
        raise ValueError("not an email address")
    return value


Email = Annotated[str, Field(max_length=320), AfterValidator(_normalise_email)]
# Max 128: argon2 handles any length, but huge inputs would only waste server time.
Password = Annotated[str, Field(min_length=8, max_length=128)]


class SignUpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Email
    password: Password
    preferred_language: Language = "en"


class LogInRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: Email
    password: Annotated[str, Field(max_length=128)]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    preferred_language: Language


def _log_in_response(response: Response, user: User) -> UserOut:
    settings = get_settings()
    token = create_token(
        user.id,
        secret=settings.secret_key,
        lifetime=timedelta(hours=settings.login_lifetime_hours),
    )
    set_login_cookie(response, token)
    return UserOut.model_validate(user)


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignUpRequest, session: DbSession, response: Response) -> UserOut:
    try:
        user = sign_up(
            session, email=body.email, password=body.password, language=body.preferred_language
        )
    except EmailTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail={"code": "email_taken"}) from None
    session.commit()
    return _log_in_response(response, user)


@router.post("/login")
def login(body: LogInRequest, session: DbSession, response: Response) -> UserOut:
    try:
        user = log_in(session, email=body.email, password=body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail={"code": "invalid_credentials"}
        ) from None
    return _log_in_response(response, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    clear_login_cookie(response)


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
