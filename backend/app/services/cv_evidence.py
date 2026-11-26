"""Saves the skills found in a CV as evidence records (M4.2).

`save_cv_evidence(session, source, index)` runs the CV finder (app/skills/cv_finder.py)
on the CV's stored text and saves one `evidence` row per finding. It returns each row
with the skill ids it names, so the next step (M4.5) can link them to skills.

Running it again on the same CV first deletes that CV's earlier evidence records (and,
by cascade, any links to them), so the result is always what the current rules find.
Other sources' evidence is never touched. Like the other services this flushes but
never commits.
"""

from dataclasses import dataclass

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import Evidence, Source
from app.skills.cv_finder import find_in_cv
from app.skills.index import SkillIndex


class NotACvError(Exception):
    """The source isn't a CV: a mistake in the calling code, not a user error, so it has
    no API error code."""


@dataclass(frozen=True)
class FoundEvidence:
    evidence: Evidence
    skill_ids: list[str]


def save_cv_evidence(session: Session, source: Source, index: SkillIndex) -> list[FoundEvidence]:
    if source.kind != "cv":
        raise NotACvError
    session.execute(delete(Evidence).where(Evidence.source_id == source.id))
    saved = []
    for finding in find_in_cv(source.text or "", index, cv_language=source.language):
        evidence = Evidence(
            user_id=source.user_id,
            source_id=source.id,
            type=finding.type,
            quote=finding.quote,
            location=finding.location,
            language=finding.language,
        )
        session.add(evidence)
        saved.append(FoundEvidence(evidence, finding.skill_ids))
    session.flush()
    return saved
