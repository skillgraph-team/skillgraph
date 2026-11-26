"""Tests for saving the skills found in a CV as evidence records (M4.2). Needs the test
database. The CV text is made up."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Evidence
from app.services.cv_evidence import NotACvError, save_cv_evidence
from app.skills.index import SkillIndex
from tests.db.factories import make_evidence, make_source, make_user

CV_TEXT = """Sam Example
Skills: Python, FastAPI, PostgreSQL and Docker.
Projects
Built a REST API with FastAPI and PostgreSQL."""


@pytest.fixture(scope="module")
def index() -> SkillIndex:
    return SkillIndex.from_csv()


def test_each_finding_becomes_an_evidence_record(db_session: Session, index: SkillIndex) -> None:
    user = make_user(db_session)
    cv = make_source(db_session, user, text=CV_TEXT, language="en")

    saved = save_cv_evidence(db_session, cv, index)

    assert [(s.evidence.type, s.skill_ids) for s in saved] == [
        ("cv_skills_list", ["python", "fastapi", "postgresql", "docker"]),
        ("cv_project", ["rest-api", "fastapi", "postgresql"]),
    ]
    project = saved[1].evidence
    assert project.quote == "Built a REST API with FastAPI and PostgreSQL."
    assert project.location == {"section": "Projects", "line": 4}
    assert project.language == "en"
    assert (project.user_id, project.source_id) == (user.id, cv.id)


def test_running_again_replaces_the_old_records(db_session: Session, index: SkillIndex) -> None:
    user = make_user(db_session)
    cv = make_source(db_session, user, text=CV_TEXT, language="en")
    first = {s.evidence.id for s in save_cv_evidence(db_session, cv, index)}

    second = {s.evidence.id for s in save_cv_evidence(db_session, cv, index)}

    stored = set(db_session.scalars(select(Evidence.id).where(Evidence.source_id == cv.id)))
    assert stored == second
    assert len(second) == 2
    assert first.isdisjoint(second)


def test_other_sources_evidence_is_untouched(db_session: Session, index: SkillIndex) -> None:
    user = make_user(db_session)
    cv = make_source(db_session, user, text=CV_TEXT, language="en")
    other_cv = make_source(db_session, user, text="Skills: Java", language="en")
    kept = make_evidence(db_session, user, other_cv)

    save_cv_evidence(db_session, cv, index)

    assert db_session.get(Evidence, kept.id) is not None


def test_a_cv_without_text_gives_no_evidence(db_session: Session, index: SkillIndex) -> None:
    cv = make_source(db_session, make_user(db_session), text=None)
    assert save_cv_evidence(db_session, cv, index) == []


def test_a_repo_source_is_refused(db_session: Session, index: SkillIndex) -> None:
    repo = make_source(db_session, make_user(db_session), kind="github_repo", title="me/app")
    with pytest.raises(NotACvError):
        save_cv_evidence(db_session, repo, index)
