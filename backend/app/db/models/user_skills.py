"""A person's skills and the evidence links behind each one
(docs/design/evidence-model.md sections 1, 3, 4 and 5).

Rules the database checks: allowed values, unverified is always low, one row per
skill per user, and a link can only join a skill and evidence of the same user.
Rules it can't check (left to the services and the validator, M4.4 / M6.3): every
skill has at least one link; status and confidence follow from the links;
`supports` is never used on a context-type evidence record.
"""

import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._columns import created_at, one_of, updated_at, user_ref, uuid_pk
from app.db.values import Confidence, Judgement, Status, System


class UserSkill(Base):
    """One skill on one person's profile, with its computed status and confidence.

    - `hidden` / `disputed`: the user's corrections (evidence model section 8).
    - `produced_by` / `agent_run_id`: which system and which run computed it.
    """

    __tablename__ = "user_skills"
    __table_args__ = (
        one_of("status", Status),
        one_of("confidence", Confidence),
        one_of("produced_by", System),
        CheckConstraint("status <> 'unverified' OR confidence = 'low'", name="unverified_is_low"),
        UniqueConstraint("user_id", "skill_id"),
        # Target of the same-user foreign key in user_skill_evidence.
        UniqueConstraint("id", "user_id"),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[user_ref]
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[str] = mapped_column(String(10))
    hidden: Mapped[bool] = mapped_column(server_default="false")
    disputed: Mapped[bool] = mapped_column(server_default="false")
    produced_by: Mapped[str] = mapped_column(String(20))
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="SET NULL")
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class UserSkillEvidence(Base):
    """An evidence link: this skill, this evidence record, `supports` or `weak`, and why.

    `user_id` appears in both foreign keys, so the skill and the evidence must belong to
    the same user: a profile can never cite someone else's evidence.
    `inferred_from`: skill ids, set when `reason_code` is `inferred_from_related`.
    """

    __tablename__ = "user_skill_evidence"
    __table_args__ = (
        one_of("judgement", Judgement),
        CheckConstraint("reason_code ~ '^[a-z][a-z_]*$'", name="reason_code_format"),
        ForeignKeyConstraint(
            ["user_skill_id", "user_id"],
            ["user_skills.id", "user_skills.user_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["evidence_id", "user_id"],
            ["evidence.id", "evidence.user_id"],
            ondelete="CASCADE",
        ),
    )

    user_skill_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    evidence_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    judgement: Mapped[str] = mapped_column(String(10))
    reason_code: Mapped[str] = mapped_column(String(50))
    inferred_from: Mapped[list[str] | None] = mapped_column(ARRAY(String(64)))
