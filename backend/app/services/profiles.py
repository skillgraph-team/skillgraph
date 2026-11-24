"""Profiles: the user's profile, and their education, experience and project lists (M3.3).

Ownership rule: every function takes the logged-in `user` and only ever touches rows
whose profile belongs to that user. An entry id from someone else's profile is treated
exactly like an id that doesn't exist (`EntryNotFoundError`), so nobody can find out
what other users have.

The profile row is created empty the first time it is needed (`get_or_create_profile`),
so there is no separate "create profile" step.

Like the other services, these functions flush but never commit; the endpoint commits.
"""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import Education, Experience, ManualProject, Profile, User

Entry = Education | Experience | ManualProject

PROFILE_FIELDS = ("display_name", "headline")
"""The profile fields a user may edit here. GitHub fields belong to M3.6 / M3.9."""


class EntryNotFoundError(Exception):
    """No entry with this id on the caller's profile (it may exist on someone else's)."""


# --- the profile -------------------------------------------------------------


def get_or_create_profile(session: Session, user: User) -> Profile:
    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        profile = Profile(user_id=user.id)
        session.add(profile)
        session.flush()
    return profile


def update_profile(session: Session, user: User, changes: dict[str, Any]) -> Profile:
    """Apply only the fields present in `changes`. `preferred_language` is stored on
    the user (it is an account setting, D-012); the rest on the profile."""
    profile = get_or_create_profile(session, user)
    if "preferred_language" in changes:
        user.preferred_language = changes["preferred_language"]
    for field in PROFILE_FIELDS:
        if field in changes:
            setattr(profile, field, changes[field])
    session.flush()
    return profile


def clear_profile(session: Session, user: User) -> None:
    """Delete the profile row. The database deletes its education, experience and
    projects with it (ON DELETE CASCADE). The account and its language stay."""
    session.execute(delete(Profile).where(Profile.user_id == user.id))
    session.flush()
    session.expire_all()  # rows loaded before the delete must not be reused


# --- education, experience, projects -----------------------------------------


def list_entries[M: Entry](session: Session, user: User, model: type[M]) -> Sequence[M]:
    """The caller's entries of one kind, in the order shown on screen."""
    query = (
        select(model)
        .join(Profile, Profile.id == model.profile_id)
        .where(Profile.user_id == user.id)
        .order_by(model.position, model.created_at, model.id)
    )
    return session.scalars(query).all()


def add_entry[M: Entry](session: Session, user: User, model: type[M], fields: dict[str, Any]) -> M:
    """Add an entry. Without a `position` it goes at the end of the list."""
    profile = get_or_create_profile(session, user)
    if fields.get("position") is None:
        last = session.scalar(
            select(func.max(model.position)).where(model.profile_id == profile.id)
        )
        fields = fields | {"position": 0 if last is None else last + 1}
    entry = model(profile_id=profile.id, **fields)
    session.add(entry)
    session.flush()
    return entry


def replace_entry[M: Entry](
    session: Session, user: User, model: type[M], entry_id: uuid.UUID, fields: dict[str, Any]
) -> M:
    """Overwrite every field of an entry. A missing `position` keeps the current one."""
    entry = _owned_entry(session, user, model, entry_id)
    if fields.get("position") is None:
        fields = {key: value for key, value in fields.items() if key != "position"}
    for field, value in fields.items():
        setattr(entry, field, value)
    session.flush()
    return entry


def delete_entry[M: Entry](
    session: Session, user: User, model: type[M], entry_id: uuid.UUID
) -> None:
    session.delete(_owned_entry(session, user, model, entry_id))
    session.flush()


def _owned_entry[M: Entry](session: Session, user: User, model: type[M], entry_id: uuid.UUID) -> M:
    """The entry with this id, only if it is on the caller's profile."""
    entry = session.scalar(
        select(model)
        .join(Profile, Profile.id == model.profile_id)
        .where(model.id == entry_id, Profile.user_id == user.id)
    )
    if entry is None:
        raise EntryNotFoundError
    return entry
