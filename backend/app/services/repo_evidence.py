"""Saves the skills found in an imported GitHub repo as evidence records (M4.3).

`save_repo_evidence(session, source, index, github_username=...)` rebuilds the repo's
`RepoInfo` from the source row (M3.6 stores it in `details`, the name in `title`), runs
the repo finder (app/skills/repo_finder.py) and replaces that repo's evidence records
with the findings (app/services/evidence_records.py).

`github_username` is the name the user gave on their profile: it decides whether the
repo counts as "owned by the person" (evidence model §3.2).
"""

from datetime import date

from sqlalchemy.orm import Session

from app.db.models import Source
from app.ingestion.github_repos import RepoInfo
from app.services.evidence_records import FoundEvidence, replace_source_evidence
from app.skills.index import SkillIndex
from app.skills.repo_finder import find_in_repo


class NotARepoError(Exception):
    """The source isn't a GitHub repo: a mistake in the calling code, not a user error,
    so it has no API error code."""


def save_repo_evidence(
    session: Session,
    source: Source,
    index: SkillIndex,
    *,
    github_username: str | None,
    today: date | None = None,
) -> list[FoundEvidence]:
    if source.kind != "github_repo":
        raise NotARepoError
    repo = RepoInfo.model_validate({**source.details, "full_name": source.title})
    findings = find_in_repo(
        repo, index, github_username=github_username, today=today or date.today()
    )
    return replace_source_evidence(session, source, findings)
