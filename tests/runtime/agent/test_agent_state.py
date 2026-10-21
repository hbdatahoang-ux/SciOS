"""
SciOS Runtime Agent State Contract Tests
========================================

Contract tests for AgentState.

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.agent.state import (
    AgentState,
    AgentStatus,
)


# ==========================================================
# Construction
# ==========================================================


def test_default_state() -> None:

    state = AgentState()

    assert state.status == AgentStatus.IDLE.value
    assert state.task is None
    assert state.error is None
    assert state.result is None


def test_agent_status_values() -> None:

    assert AgentStatus.IDLE.value == "idle"
    assert AgentStatus.RUNNING.value == "running"
    assert AgentStatus.COMPLETED.value == "completed"
    assert AgentStatus.FAILED.value == "failed"


def test_agent_status_is_string_enum() -> None:

    assert isinstance(
        AgentStatus.IDLE,
        str,
    )

    assert AgentStatus.IDLE == "idle"


# ==========================================================
# Start
# ==========================================================


def test_state_start() -> None:

    state = AgentState()

    state.start(
        "build system",
    )

    assert state.status == AgentStatus.RUNNING.value
    assert state.task == "build system"
    assert state.error is None


def test_state_start_clears_previous_error() -> None:

    state = AgentState()

    state.fail(
        ValueError("boom"),
    )

    assert state.error == "boom"

    state.start(
        "retry",
    )

    assert state.status == AgentStatus.RUNNING.value
    assert state.task == "retry"
    assert state.error is None


# ==========================================================
# Complete
# ==========================================================


def test_state_complete() -> None:

    state = AgentState()

    state.start(
        "task",
    )

    state.complete(
        "result",
    )

    assert state.status == AgentStatus.COMPLETED.value
    assert state.task == "task"
    assert state.result == "result"
    assert state.error is None


def test_state_complete_none() -> None:

    state = AgentState()

    state.complete()

    assert state.status == AgentStatus.COMPLETED.value
    assert state.result is None


# ==========================================================
# Fail
# ==========================================================


def test_state_fail() -> None:

    state = AgentState()

    error = ValueError(
        "boom",
    )

    state.fail(
        error,
    )

    assert state.status == AgentStatus.FAILED.value
    assert state.error == "boom"


def test_state_fail_stringifies_error() -> None:

    state = AgentState()

    state.fail(
        RuntimeError("runtime failure"),
    )

    assert state.error == (
        "runtime failure"
    )


# ==========================================================
# Reset
# ==========================================================


def test_state_reset() -> None:

    state = AgentState()

    state.start(
        "task",
    )

    state.complete(
        "result",
    )

    state.reset()

    assert state.status == AgentStatus.IDLE.value
    assert state.task is None
    assert state.error is None
    assert state.result is None


def test_state_reset_failed_state() -> None:

    state = AgentState()

    state.start(
        "task",
    )

    state.fail(
        ValueError("boom"),
    )

    state.reset()

    assert state.status == AgentStatus.IDLE.value
    assert state.task is None
    assert state.error is None
    assert state.result is None


# ==========================================================
# Update
# ==========================================================


def test_state_update() -> None:

    state = AgentState()

    state.update(
        status="running",
    )

    assert state.status == "running"


def test_state_update_multiple_fields() -> None:

    state = AgentState()

    state.update(
        status="completed",
        task="task",
        result="result",
    )

    assert state.status == "completed"
    assert state.task == "task"
    assert state.result == "result"


def test_state_update_ignores_unknown_fields() -> None:

    state = AgentState()

    state.update(
        unknown="value",
    )

    assert not hasattr(
        state,
        "unknown",
    )


# ==========================================================
# Serialization
# ==========================================================


def test_state_to_dict() -> None:

    state = AgentState()

    state.start(
        "task",
    )

    state.complete(
        "result",
    )

    result = state.to_dict()

    assert result == {
        "status": "completed",
        "task": "task",
        "error": None,
        "result": "result",
    }


def test_state_to_dict_is_copy() -> None:

    state = AgentState()

    state.update(
        result={
            "value": 1,
        },
    )

    result = state.to_dict()

    result["result"]["value"] = 2

    assert state.result == {
        "value": 2,
    }


# ==========================================================
# Representation
# ==========================================================


def test_state_repr() -> None:

    state = AgentState()

    text = repr(
        state,
    )

    assert "AgentState" in text
    assert "idle" in text