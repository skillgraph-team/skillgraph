"""A user's sources as a list, and deleting one (M3.7, for the sources screen).

Deleting a CV removes its file first, then the row, for the same reason as deleting an
account (T-102): if the file can't be removed, nothing is deleted and the user can try
again. The source's evidence goes with the row (ON DELETE CASCADE). Deleting a GitHub
repo source only lasts until the next import, which brings it back; withdrawing GitHub
consent removes them all (app/services/github_imports.py).

Only CVs and GitHub repos are listed and deletable here. A manual project's source is
managed with the project (app/services/manual_projects.py), so here it is "not found".
After a delete, skills left without evidence are removed and the rest recomputed
(M4.10, `recompute_skills`), in the same transaction.
"""

import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Source, User
from app.services.skill_profile import recompute_skills

LISTED_KINDS = ("cv", "github_repo")


class SourceNotFoundError(Exception):
    """No source with this id belongs to the user."""


def list_sources(session: Session, user: User) -> list[Source]:
    """Newest first; sources added at the same moment by title."""
    query = (
        select(Source)
        .where(Source.user_id == user.id, Source.kind.in_(LISTED_KINDS))
        .order_by(Source.created_at.desc(), Source.title)
    )
    return list(session.scalars(query))


def delete_source(session: Session, user: User, source_id: uuid.UUID, *, upload_dir: Path) -> None:
    source = session.scalar(
        select(Source).where(
            Source.id == source_id, Source.user_id == user.id, Source.kind.in_(LISTED_KINDS)
        )
    )
    if source is None:
        raise SourceNotFoundError
    if source.storage_path:
        # storage_path is `<user id>/<source id>.<ext>`, written by us (cv_uploads.py).
        (upload_dir / source.storage_path).unlink(missing_ok=True)
    session.delete(source)
    session.flush()
    recompute_skills(session, user)
