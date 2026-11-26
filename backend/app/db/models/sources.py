"""Sources (what we read) and evidence records (exact pieces of a source that mention
or show a skill). Definitions: docs/design/evidence-model.md sections 1, 2 and 6.
"""

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._columns import created_at, one_of, user_ref, uuid_pk
from app.db.values import EvidenceType, SourceKind, SourceLanguage

QUOTE_MAX_CHARS = 300


class Source(Base):
    """One thing we read: an uploaded CV, one GitHub repo, a certificate, a manual project.

    - `title`: file name, repo full name (`owner/repo`) or project title.
    - `details`: kind-specific facts, e.g. for a repo `owner`, `is_fork`, `languages`.
    - `storage_path`: where an uploaded file is kept, so deleting the account can remove it.
      Relative to the `UPLOAD_DIR` setting, e.g. `<user id>/<source id>.pdf`.
    - `text`: the plain text we read, in its original language: a CV's text (M3.5) or a
      repo's README (M3.6). Skill extraction (M4, M6) reads this, not the file.
    - `manual_project_id`: set exactly when `kind` is `manual_project`.
    """

    __tablename__ = "sources"
    __table_args__ = (
        one_of("kind", SourceKind),
        one_of("language", SourceLanguage, nullable=True),
        CheckConstraint(
            "(kind = 'manual_project') = (manual_project_id IS NOT NULL)",
            name="manual_project_id_iff_kind",
        ),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[user_ref]
    kind: Mapped[str] = mapped_column(String(20))
    title: Mapped[str]
    language: Mapped[str | None] = mapped_column(String(5))
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
    storage_path: Mapped[str | None]
    text: Mapped[str | None] = mapped_column(Text)
    manual_project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("manual_projects.id", ondelete="CASCADE"), unique=True
    )
    created_at: Mapped[created_at]


class Evidence(Base):
    """One evidence record: the exact quote (never translated), where it is, its type and
    language. `source_id` is empty only for `user_added` evidence (the user's own action).

    `user_id` is stored here too (not only through the source) so that links can check
    a skill and its evidence belong to the same person (see `UserSkillEvidence`).
    """

    __tablename__ = "evidence"
    __table_args__ = (
        one_of("type", EvidenceType),
        one_of("language", SourceLanguage),
        CheckConstraint(f"char_length(quote) <= {QUOTE_MAX_CHARS}", name="quote_length"),
        CheckConstraint(
            "source_id IS NOT NULL OR type = 'user_added'", name="source_unless_user_added"
        ),
        # Target of the same-user foreign key in user_skill_evidence.
        UniqueConstraint("id", "user_id"),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[user_ref]
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(30))
    quote: Mapped[str] = mapped_column(Text)
    location: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
    language: Mapped[str] = mapped_column(String(5))
    created_at: Mapped[created_at]
