"""GitHub import (M3.6, D-009: public data by username, no GitHub login).

POST /sources/github   {"username": "..."} → 200 the user's repo sources, newest push first

Imports the username's public repos as `github_repo` sources (one per repo) and saves
the username on the profile. Importing again updates them. See
app/services/github_imports.py.

Errors (body `{"detail": {"code": ...}}`):
- 422 FastAPI validation error: not a valid GitHub username
- 403 `github_consent_required`: the user hasn't agreed yet (app/api/github_consent.py)
- 404 `github_user_not_found`: no GitHub account with that name
- 429 `github_rate_limited`: GitHub's request limit is used up; `reset_at` (ISO time, or
  null) says when to try again. Setting GITHUB_TOKEN raises the limit.
- 502 `github_unavailable`: GitHub couldn't be reached or answered with an error
"""

from collections.abc import Iterator
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.current_user import CurrentUser
from app.api.sources import SourceOut
from app.config import Settings, get_settings
from app.db.session import DbSession
from app.ingestion.github_client import GitHubClient, GitHubError, GitHubRateLimitError
from app.ingestion.github_repos import GitHubUserNotFoundError
from app.services import github_imports

router = APIRouter(prefix="/sources", tags=["sources"])

# GitHub's rules: letters, digits and single hyphens between them, at most 39 characters.
GITHUB_USERNAME = r"^[A-Za-z0-9](?:-?[A-Za-z0-9])*$"


class GitHubImportIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str = Field(pattern=GITHUB_USERNAME, max_length=39)


def get_github_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[GitHubClient]:
    """One client per request. Tests replace this with a client on saved answers."""
    token = settings.github_token.get_secret_value() if settings.github_token else None
    with httpx.Client(
        base_url=settings.github_api_url, headers={"User-Agent": "skillgraph"}
    ) as http:
        yield GitHubClient(
            http,
            cache_dir=settings.github_cache_dir,
            cache_seconds=settings.github_cache_seconds,
            token=token,
        )


@router.post("/github")
def import_github(
    body: GitHubImportIn,
    user: CurrentUser,
    session: DbSession,
    client: Annotated[GitHubClient, Depends(get_github_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> list[SourceOut]:
    try:
        sources = github_imports.import_github(
            session, user, body.username, client=client, max_repos=settings.github_max_repos
        )
    except github_imports.GitHubConsentRequiredError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail={"code": error.code}) from None
    except GitHubUserNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail={"code": error.code}) from None
    except GitHubRateLimitError as error:
        reset_at = error.reset_at.isoformat() if error.reset_at else None
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, detail={"code": error.code, "reset_at": reset_at}
        ) from None
    except GitHubError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail={"code": error.code}) from None
    session.commit()
    return [SourceOut.model_validate(source) for source in sources]
