"""The run log (M5.4): one row per agent run, one row per message inside it.

A run's `user_id` is empty for evaluation runs, which have no app user. Deleting a
user deletes their runs, and a run's messages go with it (they can quote the CV).

The message envelope (D-007) is still open, so `agent_messages` keeps the whole
envelope as JSON plus a few columns for listing and ordering. M2.5 may add columns
in a new migration once the envelope is decided.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._columns import created_at, one_of, user_ref, uuid_pk
from app.db.values import Language, RunStatus, System


class AgentRun(Base):
    """One run of a workflow (`build_profile`, `find_internships`, …) by one system."""

    __tablename__ = "agent_runs"
    __table_args__ = (
        one_of("system", System),
        one_of("status", RunStatus),
        one_of("language", Language),
    )

    id: Mapped[uuid_pk]
    user_id: Mapped[user_ref | None]
    workflow: Mapped[str] = mapped_column(String(50))
    system: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    stop_reason: Mapped[str | None] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(2))
    llm_calls: Mapped[int] = mapped_column(server_default="0")
    tokens_in: Mapped[int] = mapped_column(server_default="0")
    tokens_out: Mapped[int] = mapped_column(server_default="0")
    error: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    started_at: Mapped[created_at]
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AgentMessage(Base):
    """One message in a run, in order (`sequence`). `envelope` is the full message."""

    __tablename__ = "agent_messages"
    __table_args__ = (UniqueConstraint("run_id", "sequence"),)

    id: Mapped[uuid_pk]
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True
    )
    sequence: Mapped[int]
    task_id: Mapped[uuid.UUID | None]
    parent_task_id: Mapped[uuid.UUID | None]
    sender: Mapped[str] = mapped_column(String(50))
    recipient: Mapped[str] = mapped_column(String(50))
    task: Mapped[str] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(20))
    attempt: Mapped[int] = mapped_column(server_default="1")
    envelope: Mapped[dict[str, Any]] = mapped_column(JSONB)
    tokens_in: Mapped[int] = mapped_column(server_default="0")
    tokens_out: Mapped[int] = mapped_column(server_default="0")
    duration_ms: Mapped[int | None]
    created_at: Mapped[created_at]
