"""Manual projects as evidence (M4.10): the project endpoints use these instead of the
generic entry functions in app/services/profiles.py, so that a project is always also an
evidence source.

- `add_project` / `replace_project` save the project (via profiles.py), then create or
  update its `sources` row (kind `manual_project`, title, text = title and description),
  then rebuild the user's skills (app/services/skill_profile.py). The rebuild only
  re-reads stored text (no network), so the project's new evidence is linked at once and
  its old evidence is replaced.
- `delete_project` deletes the project; its source and evidence go with it (ON DELETE
  CASCADE). Then skills left without evidence are removed and the rest recomputed.

If the skill list isn't loaded yet, a project still saves: its old evidence is removed,
and skills appear at the next build. Like the other services this flushes but never
commits.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ManualProject, Source, User
from app.ingestion.language import detect_language
from app.services import profiles
from app.services.evidence_records import replace_source_evidence
from app.services.skill_profile import SkillListNotLoadedError, build_profile, recompute_skills


def add_project(session: Session, user: User, fields: dict[str, Any]) -> ManualProject:
    project = profiles.add_entry(session, user, ManualProject, fields)
    _sync(session, user, project)
    return project


def replace_project(
    session: Session, user: User, project_id: uuid.UUID, fields: dict[str, Any]
) -> ManualProject:
    project = profiles.replace_entry(session, user, ManualProject, project_id, fields)
    _sync(session, user, project)
    return project


def delete_project(session: Session, user: User, project_id: uuid.UUID) -> None:
    profiles.delete_entry(session, user, ManualProject, project_id)
    recompute_skills(session, user)


def _sync(session: Session, user: User, project: ManualProject) -> None:
    source = session.scalar(select(Source).where(Source.manual_project_id == project.id))
    if source is None:
        source = Source(user_id=user.id, kind="manual_project", manual_project_id=project.id)
        session.add(source)
    source.title = project.title
    source.text = f"{project.title}\n{project.description}"
    source.language = detect_language(source.text)
    session.flush()
    try:
        build_profile(session, user)
    except SkillListNotLoadedError:
        replace_source_evidence(session, source, [])
        recompute_skills(session, user)
