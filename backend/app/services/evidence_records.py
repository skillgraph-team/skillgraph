"""Saves a finder's findings for one source as `evidence` rows (M4.2, M4.3).

`replace_source_evidence(session, source, findings)` deletes the source's earlier
evidence records (and, by cascade, any links to them), then adds one row per finding.
It returns each row with the skill ids it names, for the linking step (M4.5). So the
stored evidence is always what the current rules find, and other sources are never
touched. Like the other services this flushes but never commits.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import Evidence, Source
from app.skills.findings import Finding


@dataclass(frozen=True)
class FoundEvidence:
    evidence: Evidence
    skill_ids: list[str]


def replace_source_evidence(
    session: Session, source: Source, findings: Iterable[Finding]
) -> list[FoundEvidence]:
    session.execute(delete(Evidence).where(Evidence.source_id == source.id))
    saved = []
    for finding in findings:
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
