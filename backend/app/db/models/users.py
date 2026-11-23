"""Users and what they tell us about themselves: account, profile, education,
experience and manually entered projects (M3.1, M3.3).

Deleting a user deletes their profile, which deletes its education, experience and
projects (ON DELETE CASCADE all the way down).
"""

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._columns import created_at, one_of, updated_at, user_ref, uuid_pk
from app.db.values import Language


class User(Base):
    """A login. `preferred_language` is the interface and explanation language (D-012)."""

    __tablename__ = "users"
    __table_args__ = (
        one_of("preferred_language", Language),
        # Emails are stored lowercase, so the unique rule also catches "A@x.com" vs "a@x.com".
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    id: Mapped[uuid_pk]
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str]
    preferred_language: Mapped[str] = mapped_column(String(2), server_default="en")
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Profile(Base):
    """One per user. GitHub consent lives here (M3.9): import refuses while it is empty."""

    __tablename__ = "profiles"

    id: Mapped[uuid_pk]
    user_id: Mapped[user_ref] = mapped_column(unique=True)
    display_name: Mapped[str | None]
    headline: Mapped[str | None]
    github_username: Mapped[str | None] = mapped_column(String(39))
    github_consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Education(Base):
    """A degree or programme the user entered. `position` orders the list on screen."""

    __tablename__ = "education"

    id: Mapped[uuid_pk]
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    institution: Mapped[str]
    degree: Mapped[str | None]
    field_of_study: Mapped[str | None]
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int] = mapped_column(server_default="0")
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Experience(Base):
    """A job, internship or volunteering entry the user entered."""

    __tablename__ = "experience"

    id: Mapped[uuid_pk]
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    organization: Mapped[str]
    role: Mapped[str | None]
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int] = mapped_column(server_default="0")
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class ManualProject(Base):
    """A project the user described in the app. Its evidence comes through a `sources`
    row of kind `manual_project` that points back here."""

    __tablename__ = "manual_projects"

    id: Mapped[uuid_pk]
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[str | None]
    position: Mapped[int] = mapped_column(server_default="0")
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
