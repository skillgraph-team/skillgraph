"""Tests for manual projects as evidence, and for skills after a source is removed
(M4.10). Needs the test database. All data is made up."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Evidence, Skill, Source, User, UserSkill
from app.services import manual_projects
from app.services.github_imports import withdraw_consent
from app.services.skill_profile import build_profile, list_skills
from app.services.sources import delete_source
from app.skills.taxonomy import load_taxonomy
from tests.db.factories import make_profile, make_source, make_user

PROJECT = {
    "title": "Library app",
    "description": "Built a library management app with Django and PostgreSQL.",
    "url": None,
}


def statuses(session: Session, user: User) -> dict[str, tuple[str, str]]:
    return {s.skill_id: (s.status, s.confidence) for s in list_skills(session, user)}


def project_source(session: Session, project_id: object) -> Source:
    source = session.scalar(select(Source).where(Source.manual_project_id == project_id))
    assert source is not None
    return source


def new_user(session: Session) -> User:
    user = make_user(session)
    make_profile(session, user)
    return user


def test_saving_a_project_makes_it_evidence_and_skills(db_session: Session) -> None:
    load_taxonomy(db_session)
    user = new_user(db_session)

    project = manual_projects.add_project(db_session, user, PROJECT)

    source = project_source(db_session, project.id)
    assert (source.kind, source.title, source.user_id) == ("manual_project", "Library app", user.id)
    assert source.text == "Library app\nBuilt a library management app with Django and PostgreSQL."
    [evidence] = db_session.scalars(select(Evidence).where(Evidence.source_id == source.id))
    assert evidence.type == "manual_project"
    assert evidence.quote == "Built a library management app with Django and PostgreSQL."
    assert statuses(db_session, user) == {
        "django": ("demonstrated", "medium"),
        "postgresql": ("demonstrated", "medium"),
    }


def test_editing_a_project_replaces_its_evidence(db_session: Session) -> None:
    load_taxonomy(db_session)
    user = new_user(db_session)
    project = manual_projects.add_project(db_session, user, PROJECT)
    source_id = project_source(db_session, project.id).id
    old = set(db_session.scalars(select(Evidence.id).where(Evidence.source_id == source_id)))

    manual_projects.replace_project(
        db_session, user, project.id, PROJECT | {"description": "Built it again with Flask."}
    )

    assert project_source(db_session, project.id).id == source_id
    new = set(db_session.scalars(select(Evidence.id).where(Evidence.source_id == source_id)))
    assert new and new.isdisjoint(old)
    assert statuses(db_session, user) == {"flask": ("demonstrated", "medium")}


def test_deleting_a_project_removes_skills_it_alone_backed(db_session: Session) -> None:
    load_taxonomy(db_session)
    user = new_user(db_session)
    make_source(db_session, user, text="Skills: Django", language="en")
    project = manual_projects.add_project(db_session, user, PROJECT)
    assert statuses(db_session, user)["django"] == ("demonstrated", "high")

    manual_projects.delete_project(db_session, user, project.id)

    assert statuses(db_session, user) == {"django": ("claimed", "medium")}
    assert_no_skill_without_evidence(db_session)


def test_deleting_a_cv_recomputes_the_rest(db_session: Session, tmp_path: Path) -> None:
    load_taxonomy(db_session)
    user = new_user(db_session)
    cv = make_source(db_session, user, text="Skills: Django, Docker", language="en")
    manual_projects.add_project(db_session, user, PROJECT)

    delete_source(db_session, user, cv.id, upload_dir=tmp_path)

    assert statuses(db_session, user) == {
        "django": ("demonstrated", "medium"),
        "postgresql": ("demonstrated", "medium"),
    }
    assert_no_skill_without_evidence(db_session)


def test_withdrawing_github_consent_removes_repo_only_skills(
    db_session: Session, tmp_path: Path
) -> None:
    load_taxonomy(db_session)
    user = make_user(db_session)
    make_profile(db_session, user, github_username="sam")
    make_source(db_session, user, text="Skills: Python", language="en")
    make_source(
        db_session,
        user,
        kind="github_repo",
        title="sam/app",
        details={
            "owner": "sam",
            "html_url": "https://github.com/sam/app",
            "description": None,
            "is_fork": False,
            "is_archived": False,
            "default_branch": "main",
            "pushed_at": "2026-11-01T09:00:00Z",
            "topics": [],
            "languages": {"Python": 50_000, "Go": 50_000},
            "language_shares": {"Python": 50.0, "Go": 50.0},
            "commits": {"by_user": 1, "total": 1},
        },
    )
    build_profile(db_session, user)
    assert set(statuses(db_session, user)) == {"python", "go"}

    withdraw_consent(db_session, user, cache_dir=tmp_path)

    assert statuses(db_session, user) == {"python": ("claimed", "medium")}


def test_another_users_skills_are_untouched(db_session: Session, tmp_path: Path) -> None:
    load_taxonomy(db_session)
    me, other = new_user(db_session), new_user(db_session)
    other_cv = make_source(db_session, other, text="Skills: Rust", language="en")
    build_profile(db_session, other)
    mine = manual_projects.add_project(db_session, me, PROJECT)

    manual_projects.delete_project(db_session, me, mine.id)
    my_cv = make_source(db_session, me, text="Skills: Go", language="en")
    delete_source(db_session, me, my_cv.id, upload_dir=tmp_path)

    assert statuses(db_session, other) == {"rust": ("claimed", "medium")}
    assert db_session.get(Source, other_cv.id) is not None


def test_without_the_skill_list_a_project_still_saves(db_session: Session) -> None:
    db_session.query(Skill).delete()
    user = new_user(db_session)

    project = manual_projects.add_project(db_session, user, PROJECT)

    assert project_source(db_session, project.id).text.startswith("Library app")  # type: ignore[union-attr]
    assert list(db_session.scalars(select(UserSkill).where(UserSkill.user_id == user.id))) == []


def assert_no_skill_without_evidence(session: Session) -> None:
    for skill in session.scalars(select(UserSkill)):
        user = session.get(User, skill.user_id)
        assert user is not None
        view = next(s for s in list_skills(session, user) if s.id == skill.id)
        assert view.evidence, skill.skill_id
