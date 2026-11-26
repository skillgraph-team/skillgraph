"""Saves the skills found in a CV as evidence records (M4.2).

`save_cv_evidence(session, source, index)` runs the CV finder (app/skills/cv_finder.py)
on the CV's stored text and replaces that CV's evidence records with the findings (see
app/services/evidence_records.py). It returns each row with the skill ids it names, so
the next step (M4.5) can link them to skills.
"""

from sqlalchemy.orm import Session

from app.db.models import Source
from app.services.evidence_records import FoundEvidence, replace_source_evidence
from app.skills.cv_finder import find_in_cv
from app.skills.index import SkillIndex


class NotACvError(Exception):
    """The source isn't a CV: a mistake in the calling code, not a user error, so it has
    no API error code."""


def save_cv_evidence(session: Session, source: Source, index: SkillIndex) -> list[FoundEvidence]:
    if source.kind != "cv":
        raise NotACvError
    findings = find_in_cv(source.text or "", index, cv_language=source.language)
    return replace_source_evidence(session, source, findings)
