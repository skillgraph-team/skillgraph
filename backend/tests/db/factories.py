"""Small helpers that create valid database rows for tests, with made-up data.

Each `make_*` function adds one row with sensible defaults, flushes it (so it gets
its id and the database checks its constraints) and returns it. Pass keyword
arguments to override any column. Never put real people's data here.
"""

from typing import Any

from sqlalchemy.orm import Session

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

_counter = 0


def _next() -> int:
    global _counter
    _counter += 1
    return _counter


def _save[T](session: Session, row: T) -> T:
    session.add(row)
    session.flush()
    return row


def make_user(session: Session, **overrides: Any) -> User:
    values: dict[str, Any] = {
        "email": f"student{_next()}@example.com",
        "password_hash": "not-a-real-hash",
    }
    return _save(session, User(**(values | overrides)))


def make_profile(session: Session, user: User, **overrides: Any) -> Profile:
    values: dict[str, Any] = {"user_id": user.id, "display_name": "Test Student"}
    return _save(session, Profile(**(values | overrides)))


def make_education(session: Session, profile: Profile, **overrides: Any) -> Education:
    values: dict[str, Any] = {"profile_id": profile.id, "institution": "Example University"}
    return _save(session, Education(**(values | overrides)))


def make_experience(session: Session, profile: Profile, **overrides: Any) -> Experience:
    values: dict[str, Any] = {"profile_id": profile.id, "organization": "Example Startup"}
    return _save(session, Experience(**(values | overrides)))


def make_manual_project(session: Session, profile: Profile, **overrides: Any) -> ManualProject:
    values: dict[str, Any] = {
        "profile_id": profile.id,
        "title": "Library app",
        "description": "Built a library management app with Django.",
    }
    return _save(session, ManualProject(**(values | overrides)))


def make_source(session: Session, user: User, **overrides: Any) -> Source:
    values: dict[str, Any] = {"user_id": user.id, "kind": "cv", "title": "cv.pdf"}
    return _save(session, Source(**(values | overrides)))


def make_evidence(
    session: Session, user: User, source: Source | None, **overrides: Any
) -> Evidence:
    values: dict[str, Any] = {
        "user_id": user.id,
        "source_id": source.id if source else None,
        "type": "cv_skills_list",
        "quote": "Python, SQL",
        "location": {"section": "Skills", "page": 1},
        "language": "en",
    }
    return _save(session, Evidence(**(values | overrides)))


def make_skill(session: Session, **overrides: Any) -> Skill:
    n = _next()
    values: dict[str, Any] = {"id": f"skill-{n}", "name_en": f"Skill {n}"}
    return _save(session, Skill(**(values | overrides)))


def make_user_skill(session: Session, user: User, skill: Skill, **overrides: Any) -> UserSkill:
    values: dict[str, Any] = {
        "user_id": user.id,
        "skill_id": skill.id,
        "status": "claimed",
        "confidence": "medium",
        "produced_by": "rules",
    }
    return _save(session, UserSkill(**(values | overrides)))


def make_link(
    session: Session, user_skill: UserSkill, evidence: Evidence, **overrides: Any
) -> UserSkillEvidence:
    values: dict[str, Any] = {
        "user_skill_id": user_skill.id,
        "evidence_id": evidence.id,
        "user_id": user_skill.user_id,
        "judgement": "supports",
        "reason_code": "named_in_list",
    }
    return _save(session, UserSkillEvidence(**(values | overrides)))


def make_opportunity(session: Session, **overrides: Any) -> Opportunity:
    values: dict[str, Any] = {
        "title": "Backend intern",
        "organization": "Example Company",
        "kind": "internship",
        "description": "Python and PostgreSQL.",
        "language": "en",
    }
    return _save(session, Opportunity(**(values | overrides)))


def make_requirement(
    session: Session, opportunity: Opportunity, **overrides: Any
) -> OpportunityRequirement:
    values: dict[str, Any] = {
        "opportunity_id": opportunity.id,
        "raw_text": "Python",
        "importance": "required",
    }
    return _save(session, OpportunityRequirement(**(values | overrides)))


def make_match(session: Session, user: User, opportunity: Opportunity, **overrides: Any) -> Match:
    values: dict[str, Any] = {
        "user_id": user.id,
        "opportunity_id": opportunity.id,
        "produced_by": "rules",
        "language": "en",
    }
    return _save(session, Match(**(values | overrides)))


def make_run(session: Session, user: User | None, **overrides: Any) -> AgentRun:
    values: dict[str, Any] = {
        "user_id": user.id if user else None,
        "workflow": "build_profile",
        "system": "multi_agent",
        "status": "running",
        "language": "en",
    }
    return _save(session, AgentRun(**(values | overrides)))


def make_message(session: Session, run: AgentRun, **overrides: Any) -> AgentMessage:
    values: dict[str, Any] = {
        "run_id": run.id,
        "sequence": _next(),
        "sender": "orchestrator",
        "recipient": "profile",
        "task": "extract_skills",
        "envelope": {},
    }
    return _save(session, AgentMessage(**(values | overrides)))
