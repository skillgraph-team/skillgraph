"""The user's profile as a whole (M3.3).

GET    /profile  → 200 the profile with its education, experience and projects
PATCH  /profile  {display_name?, headline?, preferred_language?} → 200 the profile;
                 only the fields sent change (send null to empty a text field)
DELETE /profile  → 204; empties the profile and deletes its entries. The account and
                 its preferred language stay (deleting the account is M3.9).

A new user's profile is created empty on first use, so there is no "create" call.
`preferred_language` is stored on the user (D-012) but edited here with the rest.
The lists have their own endpoints: education.py, experience.py, projects.py.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api._fields import OptionalShortText
from app.api.current_user import CurrentUser
from app.api.education import EducationOut
from app.api.experience import ExperienceOut
from app.api.projects import ProjectOut
from app.db.models import Education, Experience, ManualProject, User
from app.db.session import DbSession
from app.db.values import Language
from app.services import profiles

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: OptionalShortText = None
    headline: OptionalShortText = None
    # Can be left out, but not set to null: every user has a language.
    preferred_language: Language = "en"


class ProfileOut(BaseModel):
    display_name: str | None
    headline: str | None
    preferred_language: Language
    education: list[EducationOut]
    experience: list[ExperienceOut]
    projects: list[ProjectOut]


def _profile_out(session: Session, user: User) -> ProfileOut:
    profile = profiles.get_or_create_profile(session, user)
    return ProfileOut(
        display_name=profile.display_name,
        headline=profile.headline,
        preferred_language=user.preferred_language,
        education=[
            EducationOut.model_validate(entry)
            for entry in profiles.list_entries(session, user, Education)
        ],
        experience=[
            ExperienceOut.model_validate(entry)
            for entry in profiles.list_entries(session, user, Experience)
        ],
        projects=[
            ProjectOut.model_validate(entry)
            for entry in profiles.list_entries(session, user, ManualProject)
        ],
    )


@router.get("")
def get_profile(user: CurrentUser, session: DbSession) -> ProfileOut:
    result = _profile_out(session, user)
    session.commit()  # keeps the empty profile created on first use
    return result


@router.patch("")
def update_profile(body: ProfileUpdate, user: CurrentUser, session: DbSession) -> ProfileOut:
    profiles.update_profile(session, user, body.model_dump(exclude_unset=True))
    session.commit()
    return _profile_out(session, user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_profile(user: CurrentUser, session: DbSession) -> None:
    profiles.clear_profile(session, user)
    session.commit()
