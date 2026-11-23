"""Deleting a user removes every row we hold about them (SPEC: account deletion).

The database does this by itself (ON DELETE CASCADE), so the test deletes the user
with plain SQL, the way M3.9's endpoint will rely on it, and then counts rows.
Shared data (skills, opportunities) and other users' data must stay.
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import (
    AgentMessage,
    AgentRun,
    Education,
    Evidence,
    Experience,
    ManualProject,
    Match,
    Opportunity,
    OpportunityRequirement,
    Profile,
    Skill,
    Source,
    User,
    UserSkill,
    UserSkillEvidence,
)
from tests.db import factories as f

# Every table that holds a user's personal data.
USER_TABLES: list[type[Base]] = [
    User,
    Profile,
    Education,
    Experience,
    ManualProject,
    Source,
    Evidence,
    UserSkill,
    UserSkillEvidence,
    Match,
    AgentRun,
    AgentMessage,
]


def build_full_user(session: Session, skill: Skill, opportunity: Opportunity) -> User:
    """A user with exactly one row in every personal-data table (three evidence rows and links)."""
    user = f.make_user(session)
    profile = f.make_profile(session, user, github_username="example-student")
    f.make_education(session, profile)
    f.make_experience(session, profile)
    project = f.make_manual_project(session, profile)
    cv = f.make_source(session, user)
    project_source = f.make_source(
        session, user, kind="manual_project", manual_project_id=project.id
    )
    from_cv = f.make_evidence(session, user, cv)
    from_project = f.make_evidence(session, user, project_source, type="manual_project")
    added = f.make_evidence(session, user, None, type="user_added", quote="Figma")
    user_skill = f.make_user_skill(session, user, skill, status="demonstrated", confidence="high")
    for evidence in (from_cv, from_project, added):
        f.make_link(session, user_skill, evidence)
    f.make_match(session, user, opportunity, gaps=[{"skill_id": skill.id}])
    run = f.make_run(session, user)
    f.make_message(session, run)
    return user


def count(session: Session, model: type[Base]) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_deleting_a_user_removes_all_their_rows(db_session: Session) -> None:
    skill = f.make_skill(db_session)
    opportunity = f.make_opportunity(db_session)
    f.make_requirement(db_session, opportunity, skill_id=skill.id)
    user = build_full_user(db_session, skill, opportunity)
    other = build_full_user(db_session, skill, opportunity)
    before = {model.__tablename__: count(db_session, model) for model in USER_TABLES}
    assert all(n >= 2 for n in before.values()), before

    db_session.execute(delete(User).where(User.id == user.id))
    db_session.expunge_all()  # forget loaded rows, so get() asks the database

    after = {model.__tablename__: count(db_session, model) for model in USER_TABLES}
    # Both users had the same rows, so exactly half of each table is left: the other user's.
    assert after == {table: n // 2 for table, n in before.items()}
    assert db_session.get(User, other.id) is not None
    # Shared data stays.
    assert db_session.get(Skill, skill.id) is not None
    assert db_session.get(Opportunity, opportunity.id) is not None
    assert count(db_session, OpportunityRequirement) == 1


def test_deleting_a_manual_project_removes_its_source_and_evidence(db_session: Session) -> None:
    user = f.make_user(db_session)
    project = f.make_manual_project(db_session, f.make_profile(db_session, user))
    source = f.make_source(db_session, user, kind="manual_project", manual_project_id=project.id)
    evidence = f.make_evidence(db_session, user, source, type="manual_project")

    db_session.execute(delete(ManualProject).where(ManualProject.id == project.id))
    db_session.expunge_all()  # forget loaded rows, so get() asks the database

    assert db_session.get(Source, source.id) is None
    assert db_session.get(Evidence, evidence.id) is None


def test_agent_runs_without_a_user_are_allowed(db_session: Session) -> None:
    """Evaluation runs (eval/) have no app user."""
    run = f.make_run(db_session, None)

    assert run.user_id is None
