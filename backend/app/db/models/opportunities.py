"""Curated postings (M1.7), the skills they ask for, and a user's match with each.

Postings and requirements are shared data. Matches are personal: deleting the user
deletes them. Gaps and recommendations are stored as JSON on the match (D-019),
because they are computed together and always read as a whole (M8.1–M8.3).
"""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._columns import created_at, one_of, updated_at, user_ref, uuid_pk
from app.db.values import Importance, Language, OpportunityKind, SourceLanguage, System


class Opportunity(Base):
    """An internship or junior job posting, collected by hand from `url`."""

    __tablename__ = "opportunities"
    __table_args__ = (one_of("kind", OpportunityKind), one_of("language", SourceLanguage))

    id: Mapped[uuid_pk]
    title: Mapped[str]
    organization: Mapped[str]
    kind: Mapped[str] = mapped_column(String(20))
    location: Mapped[str | None]
    description: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(5))
    url: Mapped[str | None]
    posted_on: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[created_at]


class OpportunityRequirement(Base):
    """One skill a posting asks for. `raw_text` is the posting's own words (original
    language); `skill_id` is empty until it's matched to the skill list."""

    __tablename__ = "opportunity_requirements"
    __table_args__ = (one_of("importance", Importance),)

    id: Mapped[uuid_pk]
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[str | None] = mapped_column(
        ForeignKey("skills.id", ondelete="RESTRICT"), index=True
    )
    raw_text: Mapped[str]
    importance: Mapped[str] = mapped_column(String(20))


class Match(Base):
    """The latest result of matching one user against one posting.

    - `score`: 0 to 1; `category`: the matching slice (M7) defines its values.
    - `details`: matched / missing / weak skills and explanation codes, as JSON.
    - `gaps`, `recommendations`: lists produced by M8.1 and M8.2, as JSON.
    - `language`: the language the explanations were written in.
    """

    __tablename__ = "matches"
    __table_args__ = (
        one_of("produced_by", System),
        one_of("language", Language),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="score_range"),
        UniqueConstraint("user_id", "opportunity_id"),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[user_ref]
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), index=True
    )
    produced_by: Mapped[str] = mapped_column(String(20))
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL")
    )
    score: Mapped[float | None]
    category: Mapped[str | None] = mapped_column(String(30))
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
    gaps: Mapped[list[Any]] = mapped_column(JSONB, server_default="[]")
    recommendations: Mapped[list[Any]] = mapped_column(JSONB, server_default="[]")
    language: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
