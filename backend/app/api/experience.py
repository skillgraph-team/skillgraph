"""The user's experience list: jobs, internships, volunteering (M3.3). Same four endpoints
as education.py and projects.py:

GET    /profile/experience             → 200 list, in screen order
POST   /profile/experience             → 201 the new entry (goes last unless `position` is set)
PUT    /profile/experience/{entry_id}  → 200 the entry, every field replaced
DELETE /profile/experience/{entry_id}  → 204

Only the caller's own entries: any other id answers 404 `not_found`.
"""

import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.api._fields import DateRange, EntryIn, OptionalLongText, OptionalShortText, ShortText
from app.api.current_user import CurrentUser
from app.db.models import Experience
from app.db.session import DbSession
from app.services import profiles

router = APIRouter(prefix="/profile/experience", tags=["profile"])


class ExperienceIn(EntryIn, DateRange):
    organization: ShortText
    role: OptionalShortText = None
    description: OptionalLongText = None


class ExperienceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization: str
    role: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
    position: int


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail={"code": "not_found"})


@router.get("")
def list_experience(user: CurrentUser, session: DbSession) -> list[ExperienceOut]:
    entries = profiles.list_entries(session, user, Experience)
    return [ExperienceOut.model_validate(entry) for entry in entries]


@router.post("", status_code=status.HTTP_201_CREATED)
def add_experience(body: ExperienceIn, user: CurrentUser, session: DbSession) -> ExperienceOut:
    entry = profiles.add_entry(session, user, Experience, body.model_dump())
    session.commit()
    return ExperienceOut.model_validate(entry)


@router.put("/{entry_id}")
def replace_experience(
    entry_id: uuid.UUID, body: ExperienceIn, user: CurrentUser, session: DbSession
) -> ExperienceOut:
    try:
        entry = profiles.replace_entry(session, user, Experience, entry_id, body.model_dump())
    except profiles.EntryNotFoundError:
        raise _not_found() from None
    session.commit()
    return ExperienceOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(entry_id: uuid.UUID, user: CurrentUser, session: DbSession) -> None:
    try:
        profiles.delete_entry(session, user, Experience, entry_id)
    except profiles.EntryNotFoundError:
        raise _not_found() from None
    session.commit()
