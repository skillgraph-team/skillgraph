"""Tests for app/agents/runtime/messages.py: the message envelope (D-007) and the task
status rules (pending → running → succeeded / failed / retrying; retrying → running)."""

from typing import Any

import pytest
from pydantic import ValidationError

from app.agents.runtime.messages import (
    AgentMessage,
    InvalidTransitionError,
    TaskError,
    allowed_next,
)


def new_message(**overrides: Any) -> AgentMessage:
    values: dict[str, Any] = {
        "sender": "orchestrator",
        "recipient": "evidence",
        "task": "judge_evidence",
        "context": {"skill_id": "python", "evidence_ids": ["e1"]},
        "expected_schema": "evidence_judgements_v1",
        "language": "fr",
    }
    return AgentMessage(**(values | overrides))


ERROR = TaskError(code="llm_invalid_json", retryable=True)


# --- the envelope ------------------------------------------------------------


def test_new_message_starts_pending_on_attempt_1_with_an_id() -> None:
    message = new_message()

    assert message.status == "pending"
    assert message.attempt == 1
    assert message.task_id is not None
    assert message.result is None and message.error is None
    assert message.created_at.tzinfo is not None


def test_every_message_gets_its_own_task_id() -> None:
    assert new_message().task_id != new_message().task_id


def test_unknown_agent_is_rejected() -> None:
    with pytest.raises(ValidationError):
        new_message(recipient="chatgpt")


def test_agent_cannot_send_to_itself() -> None:
    with pytest.raises(ValidationError):
        new_message(sender="evidence", recipient="evidence")


def test_language_must_be_en_fr_or_ar() -> None:
    with pytest.raises(ValidationError):
        new_message(language="de")


def test_task_and_schema_names_are_snake_case_codes() -> None:
    with pytest.raises(ValidationError):
        new_message(task="Judge the evidence please")
    with pytest.raises(ValidationError):
        new_message(expected_schema="Evidence Judgements")


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        new_message(priority="high")


def test_messages_are_immutable() -> None:
    message = new_message()

    with pytest.raises(ValidationError):
        message.status = "succeeded"  # type: ignore[misc]


def test_message_round_trips_through_json() -> None:
    """The run log (agent_messages.envelope) stores exactly this JSON."""
    message = new_message().start().succeed({"judgements": [{"evidence_id": "e1"}]})

    assert AgentMessage.model_validate_json(message.model_dump_json()) == message


def test_context_must_be_plain_json() -> None:
    with pytest.raises(ValidationError):
        new_message(context={"when": object()})


# --- result and error belong to the right statuses ---------------------------


def test_result_only_on_succeeded() -> None:
    with pytest.raises(ValidationError):
        new_message(result={"x": 1})
    with pytest.raises(ValidationError):
        new_message(status="succeeded")


def test_error_required_on_failed_and_retrying_only() -> None:
    with pytest.raises(ValidationError):
        new_message(status="failed")
    with pytest.raises(ValidationError):
        new_message(status="retrying")
    with pytest.raises(ValidationError):
        new_message(error=ERROR)


def test_error_code_is_a_code_not_a_sentence() -> None:
    with pytest.raises(ValidationError):
        TaskError(code="The model returned bad JSON")


# --- status rules ------------------------------------------------------------


def test_happy_path_pending_running_succeeded() -> None:
    message = new_message().start()
    assert message.status == "running"

    done = message.succeed({"ok": True})

    assert done.status == "succeeded"
    assert done.result == {"ok": True}
    assert done.task_id == message.task_id
    assert done.updated_at >= message.updated_at


def test_transitions_return_a_new_message_and_keep_the_old_one() -> None:
    pending = new_message()
    running = pending.start()

    assert pending.status == "pending"
    assert running.status == "running"


def test_failure_records_the_error() -> None:
    failed = new_message().start().fail(ERROR)

    assert failed.status == "failed"
    assert failed.error == ERROR
    assert failed.result is None


def test_retry_goes_back_to_running_with_the_next_attempt() -> None:
    retrying = new_message().start().retry(ERROR)
    assert retrying.status == "retrying"
    assert retrying.attempt == 1
    assert retrying.error == ERROR

    again = retrying.start()

    assert again.status == "running"
    assert again.attempt == 2
    assert again.error is None


def test_allowed_moves_are_exactly_the_agreed_ones() -> None:
    assert allowed_next("pending") == {"running"}
    assert allowed_next("running") == {"succeeded", "failed", "retrying"}
    assert allowed_next("retrying") == {"running"}
    assert allowed_next("succeeded") == set()
    assert allowed_next("failed") == set()


@pytest.mark.parametrize(
    ("message", "move"),
    [
        (new_message(), lambda m: m.succeed({})),  # pending → succeeded
        (new_message(), lambda m: m.fail(ERROR)),  # pending → failed
        (new_message(), lambda m: m.retry(ERROR)),  # pending → retrying
        (new_message().start(), lambda m: m.start()),  # running → running
        (new_message().start().succeed({}), lambda m: m.start()),  # succeeded → running
        (new_message().start().succeed({}), lambda m: m.fail(ERROR)),  # succeeded → failed
        (new_message().start().fail(ERROR), lambda m: m.start()),  # failed → running
        (new_message().start().retry(ERROR), lambda m: m.succeed({})),  # retrying → succeeded
    ],
)
def test_every_other_move_is_rejected(message: AgentMessage, move: Any) -> None:
    with pytest.raises(InvalidTransitionError) as raised:
        move(message)

    assert raised.value.current == message.status
