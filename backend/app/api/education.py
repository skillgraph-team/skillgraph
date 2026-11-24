"""The user's education list (M3.3). Same four endpoints as experience.py and projects.py:

GET    /profile/education             → 200 list, in screen order
POST   /profile/education             → 201 the new entry (goes last unless `position` is set)
PUT    /profile/education/{entry_id}  → 200 the entry, every field replaced
DELETE /profile/education/{entry_id}  → 204

Only the caller's own entries: any other id answers 404 `not_found`.
"""

import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.api._fields import DateRange, EntryIn, OptionalLongText, OptionalShortText, ShortText
from app.api.current_user import CurrentUser
from app.db.models import Education
from app.db.session import DbSession
from app.services import profiles

router = APIRouter(prefix="/profile/education", tags=["profile"])


class EducationIn(EntryIn, DateRange):
    institution: ShortText
    degree: OptionalShortText = None
    field_of_study: OptionalShortText = None
    description: OptionalLongText = None


class EducationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution: str
    degree: str | None
    field_of_study: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
    position: int


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail={"code": "not_found"})


@router.get("")
def list_education(user: CurrentUser, session: DbSession) -> list[EducationOut]:
    entries = profiles.list_entries(session, user, Education)
    return [EducationOut.model_validate(entry) for entry in entries]


@router.post("", status_code=status.HTTP_201_CREATED)
def add_education(body: EducationIn, user: CurrentUser, session: DbSession) -> EducationOut:
    entry = profiles.add_entry(session, user, Education, body.model_dump())
    session.commit()
    return EducationOut.model_validate(entry)


@router.put("/{entry_id}")
def replace_education(
    entry_id: uuid.UUID, body: EducationIn, user: CurrentUser, session: DbSession
) -> EducationOut:
    try:
        entry = profiles.replace_entry(session, user, Education, entry_id, body.model_dump())
    except profiles.EntryNotFoundError:
        raise _not_found() from None
    session.commit()
    return EducationOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(entry_id: uuid.UUID, user: CurrentUser, session: DbSession) -> None:
    try:
        profiles.delete_entry(session, user, Education, entry_id)
    except profiles.EntryNotFoundError:
        raise _not_found() from None
    session.commit()
