"""Tests for saving the skills found in an imported repo as evidence records (M4.3).
Needs the test database. The repo is made up."""

from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Evidence
from app.services.repo_evidence import NotARepoError, save_repo_evidence
from app.skills.index import SkillIndex
from tests.db.factories import make_source, make_user

TODAY = date(2026, 11, 26)

DETAILS = {
    "owner": "sam",
    "html_url": "https://github.com/sam/shop-api",
    "description": None,
    "is_fork": False,
    "is_archived": False,
    "default_branch": "main",
    "pushed_at": "2026-11-01T09:00:00Z",
    "topics": [],
    "languages": {"Python": 9000, "Shell": 1000},
    "language_shares": {"Python": 90.0, "Shell": 10.0},
    "commits": {"by_user": 10, "total": 10},
    "readme": {"path": "README.md", "content": "Built with FastAPI.\n", "truncated": False},
    "dependency_files": [{"path": "requirements.txt", "content": "fastapi\n", "truncated": False}],
    "file_list_truncated": False,
}


@pytest.fixture(scope="module")
def index() -> SkillIndex:
    return SkillIndex.from_csv()


def repo_source(session: Session):  # type: ignore[no-untyped-def]
    user = make_user(session)
    return make_source(
        session,
        user,
        kind="github_repo",
        title="sam/shop-api",
        details=DETAILS,
        text="Built with FastAPI.\n",
        language="en",
    )


def test_each_finding_becomes_an_evidence_record(db_session: Session, index: SkillIndex) -> None:
    repo = repo_source(db_session)

    saved = save_repo_evidence(db_session, repo, index, github_username="sam", today=TODAY)

    assert [(s.evidence.type, s.evidence.quote, s.skill_ids) for s in saved] == [
        ("repo_language", "Python 90%", ["python"]),
        ("repo_language", "Shell 10%", ["bash"]),
        ("repo_dependency", "fastapi", ["fastapi"]),
        ("repo_readme", "Built with FastAPI.", ["fastapi"]),
    ]
    assert saved[0].evidence.location["owned"] is True
    assert {s.evidence.source_id for s in saved} == {repo.id}


def test_running_again_replaces_the_old_records(db_session: Session, index: SkillIndex) -> None:
    repo = repo_source(db_session)
    save_repo_evidence(db_session, repo, index, github_username="sam", today=TODAY)

    second = save_repo_evidence(db_session, repo, index, github_username="sam", today=TODAY)

    stored = set(db_session.scalars(select(Evidence.id).where(Evidence.source_id == repo.id)))
    assert stored == {s.evidence.id for s in second}
    assert len(stored) == 4


def test_a_cv_source_is_refused(db_session: Session, index: SkillIndex) -> None:
    cv = make_source(db_session, make_user(db_session))
    with pytest.raises(NotARepoError):
        save_repo_evidence(db_session, cv, index, github_username="sam", today=TODAY)
