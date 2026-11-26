"""Consent to importing GitHub data (M3.9). The import (`POST /sources/github`) answers
403 `github_consent_required` until the user has agreed here.

GET    /profile/github-consent → 200 {consented_at, github_username}
PUT    /profile/github-consent → 200 the same; records the time of consent (agreeing
                                 again keeps the first time)
DELETE /profile/github-consent → 204; withdraws consent and deletes everything imported
                                 from GitHub (repo sources, the username, cached answers)

The frontend shows the consent text (what is read, that it's public data, how to take
it back) before calling PUT. The service: app/services/github_imports.py.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.current_user import CurrentUser
from app.config import Settings, get_settings
from app.db.models import Profile
from app.db.session import DbSession
from app.services import github_imports
from app.services.profiles import get_or_create_profile

router = APIRouter(prefix="/profile/github-consent", tags=["profile"])


class GitHubConsentOut(BaseModel):
    consented_at: datetime | None
    github_username: str | None


def _out(profile: Profile) -> GitHubConsentOut:
    return GitHubConsentOut(
        consented_at=profile.github_consent_at, github_username=profile.github_username
    )


@router.get("")
def get_consent(user: CurrentUser, session: DbSession) -> GitHubConsentOut:
    profile = get_or_create_profile(session, user)
    session.commit()
    return _out(profile)


@router.put("")
def give_consent(user: CurrentUser, session: DbSession) -> GitHubConsentOut:
    profile = github_imports.give_consent(session, user)
    session.commit()
    return _out(profile)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_consent(
    user: CurrentUser,
    session: DbSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    github_imports.withdraw_consent(session, user, cache_dir=settings.github_cache_dir)
    session.commit()
