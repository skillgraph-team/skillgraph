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
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Source, User
from app.ingestion.github_client import GitHubClient
from app.ingestion.github_repos import RepoInfo, fetch_repos
from app.ingestion.language import detect_language
from app.services.profiles import get_or_create_profile


def import_github(
    session: Session, user: User, username: str, *, client: GitHubClient, max_repos: int
) -> Sequence[Source]:
    repos = fetch_repos(client, username, max_repos=max_repos)  # may raise; nothing saved yet

    get_or_create_profile(session, user).github_username = username
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
