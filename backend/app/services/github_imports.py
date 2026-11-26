"""GitHub import (M3.6): fetch a username's public repos and save one `sources` row per
repo (kind `github_repo`). How the repos are read: app/ingestion/github_repos.py.

Each source row:
- `title`: the repo's full name, `owner/repo`;
- `text`: the README, exactly as written (empty when there is none);
- `language`: the README's language (en / fr / ar / other); `other` without a README,
  since code itself counts as `other`;
- `details`: everything else from `RepoInfo` (fork flag, language shares, topics,
  commit counts, dependency files...).

Importing again updates the same rows (matched by repo name), so their ids and the
evidence pointing at them stay. Repos that are gone, or belonged to an earlier
username, are deleted with their evidence. The username is saved on the profile.

Nothing is saved if GitHub fails part-way: the error is raised before any row is
touched. Like the other services this flushes but never commits.

Consent (M3.9): the import refuses (`GitHubConsentRequiredError`) until the user has
agreed (`give_consent`, stored as `profiles.github_consent_at`). `withdraw_consent`
takes it back and deletes everything imported from GitHub: the repo sources (and
their evidence, by cascade), the saved username, and the cached GitHub answers.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import Profile, Source, User
from app.ingestion.github_client import GitHubClient, forget_cached_user
from app.ingestion.github_repos import RepoInfo, fetch_repos
from app.ingestion.language import detect_language
from app.services.profiles import get_or_create_profile


class GitHubConsentRequiredError(Exception):
    """The user hasn't agreed to their GitHub data being imported."""

    code = "github_consent_required"


def import_github(
    session: Session, user: User, username: str, *, client: GitHubClient, max_repos: int
) -> Sequence[Source]:
    profile = get_or_create_profile(session, user)
    if profile.github_consent_at is None:
        raise GitHubConsentRequiredError  # checked before asking GitHub anything
    repos = fetch_repos(client, username, max_repos=max_repos)  # may raise; nothing saved yet

    profile.github_username = username
    existing = {
        source.title.lower(): source
        for source in session.scalars(
            select(Source).where(Source.user_id == user.id, Source.kind == "github_repo")
        )
    }
    saved = []
    for repo in repos:
        source = existing.pop(repo.full_name.lower(), None)
        if source is None:
            source = Source(user_id=user.id, kind="github_repo")
            session.add(source)
        _fill(source, repo)
        saved.append(source)
    for gone in existing.values():
        session.delete(gone)
    session.flush()
    return saved


def _fill(source: Source, repo: RepoInfo) -> None:
    readme = repo.readme.content if repo.readme else None
    source.title = repo.full_name
    source.text = readme
    source.language = detect_language(readme) if readme else "other"
    source.details = repo.model_dump(mode="json", exclude={"full_name"})


def give_consent(session: Session, user: User) -> Profile:
    """Record that the user agrees. Agreeing again keeps the first time."""
    profile = get_or_create_profile(session, user)
    if profile.github_consent_at is None:
        profile.github_consent_at = datetime.now(UTC)
        session.flush()
    return profile


def withdraw_consent(session: Session, user: User, *, cache_dir: Path) -> None:
    profile = get_or_create_profile(session, user)
    username = profile.github_username
    session.execute(delete(Source).where(Source.user_id == user.id, Source.kind == "github_repo"))
    profile.github_consent_at = None
    profile.github_username = None
    session.flush()
    session.expire_all()  # sources loaded before the delete must not be reused
    if username:
        forget_cached_user(cache_dir, username)
