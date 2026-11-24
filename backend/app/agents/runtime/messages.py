"""The message envelope agents and the orchestrator exchange, and the task status rules.

Contract D-007 (owner: Rasen). Every task an agent works on is one `AgentMessage`:
the orchestrator creates it (`pending`), and each step of its life is a new, immutable
copy made by one of the transition methods:

    pending  --start()-->   running
    running  --succeed()--> succeeded           (final)
    running  --fail()-->    failed              (final)
    running  --retry()-->   retrying
    retrying --start()-->   running, attempt + 1

Any other move raises `InvalidTransitionError`. The run log (M5.4) saves every copy as
one `agent_messages` row, so a run can be replayed step by step.

What goes in the envelope:
- `context` and `result` are plain JSON (no database objects): agents only see what
  they are given. `result` is the agent's pydantic answer, dumped with
  `model_dump(mode="json")`; the runtime (M5.1) checks it against `expected_schema`.
- `expected_schema` is the *name* of the answer model (e.g. `evidence_judgements_v1`),
  not a full JSON Schema, so logs stay short; the runtime looks the model up by name.
- `error` is a code plus a developer note. It's never shown to users as is; the
  frontend translates the code.
- `language` is the language the agent must write in (D-012). Quotes stay as they are.
"""

from datetime import UTC, datetime
from typing import Any, Literal, Self, get_args
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from app.db.values import Language

AgentName = Literal[
    "orchestrator",
    "profile",
    "evidence",
    "opportunity",
    "matching",
    "development",
    "single_agent",
]
"""Who can send or receive a message. `single_agent` is System B (one agent does it all)."""

TaskStatus = Literal["pending", "running", "succeeded", "failed", "retrying"]

_ALLOWED: dict[str, frozenset[str]] = {
    "pending": frozenset({"running"}),
    "running": frozenset({"succeeded", "failed", "retrying"}),
    "retrying": frozenset({"running"}),
    "succeeded": frozenset(),
    "failed": frozenset(),
}
assert set(_ALLOWED) == set(get_args(TaskStatus))

# Lowercase snake_case codes, e.g. `judge_evidence`, `evidence_judgements_v1`.
_CODE = r"^[a-z][a-z0-9_]*$"


def allowed_next(status: TaskStatus) -> set[str]:
    """The statuses a task in `status` may move to."""
    return set(_ALLOWED[status])


def _now() -> datetime:
    return datetime.now(UTC)


class InvalidTransitionError(Exception):
    """A status move the rules don't allow (e.g. succeeded → running)."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"task status cannot go from {current!r} to {target!r}")
        self.current = current
        self.target = target


class TaskError(BaseModel):
    """Why a task failed. `retryable` tells the orchestrator a retry may help."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern=_CODE, max_length=64)
    detail: str | None = Field(default=None, max_length=2000)
    retryable: bool = False


class AgentMessage(BaseModel):
    """One task, sent from `sender` to `recipient`. Immutable: transitions return a copy."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: UUID = Field(default_factory=uuid4)
    parent_task_id: UUID | None = None
    sender: AgentName
    recipient: AgentName
    task: str = Field(pattern=_CODE, max_length=100)
    context: dict[str, JsonValue] = Field(default_factory=dict)
    expected_schema: str = Field(pattern=_CODE, max_length=100)
    status: TaskStatus = "pending"
    result: dict[str, JsonValue] | None = None
    error: TaskError | None = None
    attempt: int = Field(default=1, ge=1)
    language: Language
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        if self.sender == self.recipient:
            raise ValueError("sender and recipient must differ")
        if (self.result is not None) != (self.status == "succeeded"):
            raise ValueError("result is required when succeeded, and only then")
        if (self.error is not None) != (self.status in ("failed", "retrying")):
            raise ValueError("error is required when failed or retrying, and only then")
        return self

    # --- transitions -----------------------------------------------------------

    def start(self) -> "AgentMessage":
        """pending → running, or retrying → running (next attempt)."""
        attempt = self.attempt + 1 if self.status == "retrying" else self.attempt
        return self._move("running", attempt=attempt, error=None)

    def succeed(self, result: dict[str, JsonValue]) -> "AgentMessage":
        """running → succeeded, with the agent's answer."""
        return self._move("succeeded", result=result)

    def fail(self, error: TaskError) -> "AgentMessage":
        """running → failed (final)."""
        return self._move("failed", error=error)

    def retry(self, error: TaskError) -> "AgentMessage":
        """running → retrying: this attempt failed, another one will follow."""
        return self._move("retrying", error=error)

    def _move(self, target: TaskStatus, **changes: Any) -> "AgentMessage":
        if target not in _ALLOWED[self.status]:
            raise InvalidTransitionError(self.status, target)
        # Re-validate (model_copy would skip the checks above).
        return AgentMessage.model_validate(
            self.model_dump() | changes | {"status": target, "updated_at": _now()}
        )
