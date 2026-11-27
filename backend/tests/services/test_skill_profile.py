"""Tests for building a user's skills from their sources (M4.5): finders → judgement →
status rules → saved skills and evidence links. Needs the test database. All data is
made up."""

from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.db.models import Skill, User, UserSkill
from app.services.skill_profile import (
    SkillListNotLoadedError,
    UserSkillNotFoundError,
    build_profile,
    list_skills,
    update_skill,
)
from app.skills.taxonomy import load_taxonomy
from tests.db.factories import make_profile, make_source, make_user

TODAY = date(2026, 11, 26)

CV_TEXT = """Sam Example
Skills: Python, FastAPI, Docker
Projects
Built a REST API with FastAPI and PostgreSQL.
Education
Licence Informatique, module Bases de données"""

REPO_DETAILS = {
    "owner": "sam",
    "html_url": "https://github.com/sam/shop-api",
    "description": None,
    "is_fork": False,
    "is_archived": False,
    "default_branch": "main",
    "pushed_at": "2026-11-01T09:00:00Z",
    "topics": [],
    "languages": {"Python": 90_000, "Shell": 6_000},
    "language_shares": {"Python": 93.8, "Shell": 6.2},
    "commits": {"by_user": 10, "total": 10},
    "readme": None,
    "dependency_files": [
        {"path": "requirements.txt", "content": "fastapi\npsycopg\n", "truncated": False}
    ],
    "file_list_truncated": False,
}


@pytest.fixture
def user(db_session: Session) -> User:
    load_taxonomy(db_session)
    user = make_user(db_session)
    make_profile(db_session, user, github_username="sam")
    make_source(db_session, user, text=CV_TEXT, language="en")
    make_source(db_session, user, kind="github_repo", title="sam/shop-api", details=REPO_DETAILS)
    return user


def snapshot(session: Session, user: User) -> list[tuple[object, ...]]:
    """Everything that matters about the result, without database ids."""
    return [
        (
            s.skill_id,
            s.status,
            s.confidence,
            s.reason.code,
            sorted((e.type, e.quote, e.judgement, e.reason_code) for e in s.evidence),
        )
        for s in list_skills(session, user)
    ]


def statuses(session: Session, user: User) -> dict[str, tuple[str, str]]:
    return {s.skill_id: (s.status, s.confidence) for s in list_skills(session, user)}


def test_build_gives_each_skill_its_status_and_confidence(db_session: Session, user: User) -> None:
    build_profile(db_session, user, today=TODAY)
    assert statuses(db_session, user) == {
        # CV list + repo language 93.8 % in an owned repo
        "python": ("demonstrated", "high"),
        # CV list + concrete CV project; the dependency doesn't count
        "fastapi": ("demonstrated", "high"),
        "rest-api": ("demonstrated", "medium"),
        "postgresql": ("demonstrated", "medium"),
        "docker": ("claimed", "medium"),
        # only 6.2 % of the repo
        "bash": ("unverified", "low"),
        "databases": ("unverified", "low"),
    }


def test_each_skill_lists_its_evidence_with_the_judgement(db_session: Session, user: User) -> None:
    build_profile(db_session, user, today=TODAY)
    python = next(s for s in list_skills(db_session, user) if s.skill_id == "python")
    assert sorted((e.type, e.judgement, e.reason_code) for e in python.evidence) == [
        ("cv_skills_list", "supports", "named_in_list"),
        ("repo_language", "supports", "language_share_ok"),
    ]
    assert python.reason.code == "language_share_ok"
    assert python.reason.evidence_id in {e.id for e in python.evidence}


def test_building_twice_gives_identical_results(db_session: Session, user: User) -> None:
    build_profile(db_session, user, today=TODAY)
    first = snapshot(db_session, user)
    first_ids = {s.id for s in list_skills(db_session, user)}

    build_profile(db_session, user, today=TODAY)

    assert snapshot(db_session, user) == first
    assert {s.id for s in list_skills(db_session, user)} == first_ids


def test_corrections_survive_a_rebuild(db_session: Session, user: User) -> None:
    build_profile(db_session, user, today=TODAY)
    docker = next(s for s in list_skills(db_session, user) if s.skill_id == "docker")
    update_skill(db_session, user, docker.id, hidden=True, disputed=True, note="Only a course")

    build_profile(db_session, user, today=TODAY)

    again = next(s for s in list_skills(db_session, user) if s.skill_id == "docker")
    assert (again.id, again.hidden, again.disputed, again.note) == (
        docker.id,
        True,
        True,
        "Only a course",
    )
    assert (again.status, again.confidence) == ("claimed", "medium")


def test_a_skill_whose_evidence_is_gone_is_removed(db_session: Session, user: User) -> None:
    build_profile(db_session, user, today=TODAY)
    cv = next(s for s in user_sources(db_session, user) if s.kind == "cv")
    db_session.delete(cv)
    db_session.flush()

    build_profile(db_session, user, today=TODAY)

    found = statuses(db_session, user)
    assert "docker" not in found
    assert found["python"] == ("demonstrated", "medium")


def test_no_sources_gives_no_skills(db_session: Session) -> None:
    load_taxonomy(db_session)
    user = make_user(db_session)
    assert build_profile(db_session, user, today=TODAY) == []


def test_the_skill_list_must_be_loaded(db_session: Session) -> None:
    db_session.query(Skill).delete()
    user = make_user(db_session)
    with pytest.raises(SkillListNotLoadedError):
        build_profile(db_session, user, today=TODAY)


def test_updating_someone_elses_skill_is_refused(db_session: Session, user: User) -> None:
    build_profile(db_session, user, today=TODAY)
    skill = list_skills(db_session, user)[0]
    other = make_user(db_session)
    with pytest.raises(UserSkillNotFoundError):
        update_skill(db_session, other, skill.id, hidden=True)
    assert db_session.get(UserSkill, skill.id).hidden is False  # type: ignore[union-attr]


def user_sources(session: Session, user: User):  # type: ignore[no-untyped-def]
    from app.db.models import Source

    return session.query(Source).filter(Source.user_id == user.id).all()
