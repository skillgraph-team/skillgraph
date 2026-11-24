"""Projects the user describes by hand (M3.3). Same four endpoints as education.py and
experience.py:

GET    /profile/projects             → 200 list, in screen order
POST   /profile/projects             → 201 the new project (goes last unless `position` is set)
PUT    /profile/projects/{entry_id}  → 200 the project, every field replaced
DELETE /profile/projects/{entry_id}  → 204

Only the caller's own projects: any other id answers 404 `not_found`.

Stored in the `manual_projects` table. Turning a project into evidence (its `sources`
row of kind `manual_project`) is left to the evidence slices; deleting a project already
deletes that source and its evidence (ON DELETE CASCADE).
"""

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.api._fields import EntryIn, LongText, ShortText, WebUrl
from app.api.current_user import CurrentUser
from app.db.models import ManualProject
from app.db.session import DbSession
from app.services import profiles

router = APIRouter(prefix="/profile/projects", tags=["profile"])


class ProjectIn(EntryIn):
    title: ShortText
    description: LongText
    url: WebUrl | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    url: str | None
    position: int


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail={"code": "not_found"})


@router.get("")
def list_projects(user: CurrentUser, session: DbSession) -> list[ProjectOut]:
    entries = profiles.list_entries(session, user, ManualProject)
    return [ProjectOut.model_validate(entry) for entry in entries]


@router.post("", status_code=status.HTTP_201_CREATED)
def add_project(body: ProjectIn, user: CurrentUser, session: DbSession) -> ProjectOut:
    entry = profiles.add_entry(session, user, ManualProject, body.model_dump())
    session.commit()
    return ProjectOut.model_validate(entry)


@router.put("/{entry_id}")
def replace_project(
    entry_id: uuid.UUID, body: ProjectIn, user: CurrentUser, session: DbSession
) -> ProjectOut:
    try:
        entry = profiles.replace_entry(session, user, ManualProject, entry_id, body.model_dump())
    except profiles.EntryNotFoundError:
        raise _not_found() from None
    session.commit()
    return ProjectOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(entry_id: uuid.UUID, user: CurrentUser, session: DbSession) -> None:
    try:
        profiles.delete_entry(session, user, ManualProject, entry_id)
    except profiles.EntryNotFoundError:
        raise _not_found() from None
    session.commit()
