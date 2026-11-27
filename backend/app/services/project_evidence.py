"""Saves the skills found in a manual project as evidence records (M4.10).

`save_project_evidence(session, source, index)` reads the project behind a
`manual_project` source, runs the project finder (app/skills/project_finder.py) on its
title and description, and replaces that source's evidence records with the findings
(app/services/evidence_records.py), like the CV and repo savers.
"""

from sqlalchemy.orm import Session

from app.db.models import ManualProject, Source
from app.services.evidence_records import FoundEvidence, replace_source_evidence
from app.skills.index import SkillIndex
from app.skills.project_finder import find_in_project


class NotAProjectError(Exception):
    """The source isn't a manual project: a mistake in the calling code, so it has no API
    error code."""


def save_project_evidence(
    session: Session, source: Source, index: SkillIndex
) -> list[FoundEvidence]:
    if source.kind != "manual_project" or source.manual_project_id is None:
        raise NotAProjectError
    project = session.get(ManualProject, source.manual_project_id)
    if project is None:
        raise NotAProjectError
    findings = find_in_project(
        project.title, project.description, index, project_id=str(project.id)
    )
    return replace_source_evidence(session, source, findings)
