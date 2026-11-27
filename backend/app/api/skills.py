"""The user's skills (M4.5), built by System A from their CVs and GitHub repos.

POST  /skills/build  → 200 the skills, freshly built from all the user's sources. Running
                       it again gives the same result and keeps the corrections below.
GET   /skills        → 200 the skills, strongest first (status, then confidence, then name)
PATCH /skills/{id}   → 200 the skill. Body: any of `hidden`, `disputed` (true / false) and
                       `note` (≤ 500 characters, or null to clear). Status and confidence
                       can't be changed (any other field → 422).
                       Only the caller's own skills: any other id answers 404 `not_found`.

Each skill: `id`, `skill_id`, `names` (en / fr / ar), `category`, `status`, `confidence`,
`reason` (`code` plus `evidence_id`, for the screen to explain), `hidden`, `disputed`,
`note`, and `evidence` (each quote with its type, location, language, `judgement` and
`reason_code`). Quotes are never translated.

Errors (body `{"detail": {"code": ...}}`):
- 503 `skill_list_not_loaded`: the skill list isn't in the database yet
  (`uv run python -m app.skills.taxonomy`)

How skills are built: app/services/skill_profile.py.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, StringConstraints

from app.api.current_user import CurrentUser
from app.db.session import DbSession
from app.services import skill_profile
from app.services.skill_profile import SkillView

router = APIRouter(prefix="/skills", tags=["skills"])

NOTE_MAX_CHARS = 500
Note = Annotated[str, StringConstraints(strip_whitespace=True, max_length=NOTE_MAX_CHARS)]


class SkillCorrectionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hidden: bool | None = None
    disputed: bool | None = None
    note: Note | None = None


@router.post("/build")
def build_skills(user: CurrentUser, session: DbSession) -> list[SkillView]:
    try:
        skills = skill_profile.build_profile(session, user)
    except skill_profile.SkillListNotLoadedError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "skill_list_not_loaded"}
        ) from None
    session.commit()
    return skills


@router.get("")
def list_skills(user: CurrentUser, session: DbSession) -> list[SkillView]:
    return skill_profile.list_skills(session, user)


@router.patch("/{user_skill_id}")
def correct_skill(
    user_skill_id: uuid.UUID, body: SkillCorrectionIn, user: CurrentUser, session: DbSession
) -> SkillView:
    changes = body.model_dump(exclude_unset=True)
    for flag in ("hidden", "disputed"):
        if flag in changes and changes[flag] is None:
            changes.pop(flag)  # null means "no change" for a flag; only the note can be cleared
    if "note" in changes and not changes["note"]:
        changes["note"] = None
    try:
        skill = skill_profile.update_skill(session, user, user_skill_id, **changes)
    except skill_profile.UserSkillNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail={"code": "not_found"}) from None
    session.commit()
    return skill
