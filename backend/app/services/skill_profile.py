"""Builds a user's skills from their sources with System A, the fixed rules (M4.5), and
reads them back with their evidence.

`build_profile(session, user)` does, in order:
1. For each of the user's CVs and GitHub repos, run its finder and replace that source's
   evidence records (app/services/cv_evidence.py, repo_evidence.py).
2. Judge every link (evidence × skill) with `judge` (app/skills/judge.py).
3. For each skill, compute status and confidence from its links (app/skills/status_rules.py)
   and save the `user_skills` row and its `user_skill_evidence` links.

Running it again gives the same result. Skill rows are updated in place, so their ids
and the user's corrections (hidden, disputed, note) stay. A skill none of the evidence
names any more is deleted ("no skill without a source"). Manual projects and
user-added skills aren't read yet (M4.10 and a later slice).

`list_skills` returns each skill with its names, status, confidence, the reason (a code
and the evidence id, computed from the links, so it can't go stale), the corrections, and
its evidence. `update_skill` changes only the corrections; status and confidence never.

Like the other services this flushes but never commits.
"""

import uuid
from collections import defaultdict
from datetime import date
from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Evidence, Profile, Skill, Source, User, UserSkill, UserSkillEvidence
from app.db.values import Confidence, EvidenceType, Judgement, SourceLanguage, Status
from app.services.cv_evidence import save_cv_evidence
from app.services.evidence_records import FoundEvidence
from app.services.repo_evidence import save_repo_evidence
from app.skills.index import load_index
from app.skills.judge import judge
from app.skills.status_rules import CONFIDENCE_ORDER, STATUS_ORDER, Link, compute

CORRECTIONS = frozenset({"hidden", "disputed", "note"})


class SkillListNotLoadedError(Exception):
    """The `skills` table is empty: run `uv run python -m app.skills.taxonomy` first."""

    code = "skill_list_not_loaded"


class UserSkillNotFoundError(Exception):
    """No skill with this id on this user's profile."""


class EvidenceView(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID | None
    type: EvidenceType
    quote: str
    location: dict[str, Any]
    language: SourceLanguage
    judgement: Judgement
    reason_code: str


class ReasonView(BaseModel):
    code: str
    evidence_id: uuid.UUID | None


class SkillView(BaseModel):
    id: uuid.UUID
    skill_id: str
    names: dict[str, str]
    """{"en": ..., "fr": ..., "ar": ...}; the screen shows the one for its language."""
    category: str | None
    status: Status
    confidence: Confidence
    reason: ReasonView
    hidden: bool
    disputed: bool
    note: str | None
    evidence: list[EvidenceView]


# --- building ------------------------------------------------------------------------------


def build_profile(session: Session, user: User, *, today: date | None = None) -> list[SkillView]:
    if not session.scalar(select(func.count()).select_from(Skill)):
        raise SkillListNotLoadedError
    found = _find_evidence(session, user, today=today)

    links_by_skill: dict[str, list[tuple[Evidence, Link]]] = defaultdict(list)
    for item in found:
        evidence = item.evidence
        judged = judge(evidence.type, evidence.quote, evidence.location)  # type: ignore[arg-type]
        link = Link(
            evidence_id=str(evidence.id),
            source_id=str(evidence.source_id) if evidence.source_id else None,
            type=evidence.type,
            judgement=judged.judgement,
            reason_code=judged.reason_code,
            location=evidence.location,
        )
        for skill_id in item.skill_ids:
            links_by_skill[skill_id].append((evidence, link))

    existing = {
        row.skill_id: row
        for row in session.scalars(select(UserSkill).where(UserSkill.user_id == user.id))
    }
    for skill_id, row in existing.items():
        if skill_id not in links_by_skill:
            session.delete(row)
    session.flush()

    for skill_id, pairs in links_by_skill.items():
        result = compute([link for _, link in pairs])
        row = existing.get(skill_id) or UserSkill(user_id=user.id, skill_id=skill_id)
        row.status, row.confidence, row.produced_by = result.status, result.confidence, "rules"
        session.add(row)
        session.flush()
        # The old links went with the old evidence records (ON DELETE CASCADE).
        session.add_all(
            UserSkillEvidence(
                user_skill_id=row.id,
                evidence_id=evidence.id,
                user_id=user.id,
                judgement=link.judgement,
                reason_code=link.reason_code,
            )
            for evidence, link in pairs
        )
    session.flush()
    return list_skills(session, user)


def _find_evidence(session: Session, user: User, *, today: date | None) -> list[FoundEvidence]:
    index = load_index(session)
    username = session.scalar(select(Profile.github_username).where(Profile.user_id == user.id))
    sources = session.scalars(
        select(Source).where(Source.user_id == user.id).order_by(Source.created_at, Source.id)
    )
    found: list[FoundEvidence] = []
    for source in sources:
        if source.kind == "cv":
            found += save_cv_evidence(session, source, index)
        elif source.kind == "github_repo":
            found += save_repo_evidence(
                session, source, index, github_username=username, today=today
            )
    return found


# --- reading and correcting -------------------------------------------------------------------


def list_skills(session: Session, user: User) -> list[SkillView]:
    rows = session.execute(
        select(UserSkill, Skill)
        .join(Skill, Skill.id == UserSkill.skill_id)
        .where(UserSkill.user_id == user.id)
    ).all()
    evidence_by_skill = _evidence_by_skill(session, user)
    views = [_view(row, skill, evidence_by_skill[row.id]) for row, skill in rows]
    return sorted(
        views,
        key=lambda v: (
            -STATUS_ORDER[v.status],
            -CONFIDENCE_ORDER[v.confidence],
            v.names["en"].lower(),
        ),
    )


def update_skill(
    session: Session, user: User, user_skill_id: uuid.UUID, **changes: Any
) -> SkillView:
    unknown = set(changes) - CORRECTIONS
    if unknown:
        raise ValueError(f"only corrections can change, not {sorted(unknown)}")
    row = session.get(UserSkill, user_skill_id)
    if row is None or row.user_id != user.id:
        raise UserSkillNotFoundError
    for field, value in changes.items():
        setattr(row, field, value)
    session.flush()
    skill = session.get(Skill, row.skill_id)
    assert skill is not None  # the foreign key guarantees it
    return _view(row, skill, _evidence_by_skill(session, user)[row.id])


def _evidence_by_skill(session: Session, user: User) -> dict[uuid.UUID, list[EvidenceView]]:
    out: dict[uuid.UUID, list[EvidenceView]] = defaultdict(list)
    rows = session.execute(
        select(UserSkillEvidence, Evidence)
        .join(Evidence, Evidence.id == UserSkillEvidence.evidence_id)
        .where(UserSkillEvidence.user_id == user.id)
    ).all()
    for link, evidence in rows:
        out[link.user_skill_id].append(
            EvidenceView(
                id=evidence.id,
                source_id=evidence.source_id,
                type=evidence.type,
                quote=evidence.quote,
                location=evidence.location,
                language=evidence.language,
                judgement=link.judgement,
                reason_code=link.reason_code,
            )
        )
    for items in out.values():  # supporting evidence first, then a fixed order
        items.sort(key=lambda e: (e.judgement != "supports", e.type, e.quote, str(e.id)))
    return out


def _view(row: UserSkill, skill: Skill, evidence: list[EvidenceView]) -> SkillView:
    result = compute(
        [
            Link(
                evidence_id=str(e.id),
                source_id=str(e.source_id) if e.source_id else None,
                type=e.type,
                judgement=e.judgement,
                reason_code=e.reason_code,
                location=e.location,
            )
            for e in evidence
        ]
    )
    reason_id = uuid.UUID(result.reason.evidence_id) if result.reason.evidence_id else None
    return SkillView(
        id=row.id,
        skill_id=row.skill_id,
        names={
            "en": skill.name_en,
            "fr": skill.name_fr or skill.name_en,
            "ar": skill.name_ar or skill.name_en,
        },
        category=skill.category,
        status=row.status,
        confidence=row.confidence,
        reason=ReasonView(code=result.reason.code, evidence_id=reason_id),
        hidden=row.hidden,
        disputed=row.disputed,
        note=row.note,
        evidence=evidence,
    )
