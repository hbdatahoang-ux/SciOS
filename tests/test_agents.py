"""
SciOS Agent Tests
=================

Unit tests for the SciOS Agent abstraction.

These tests validate the stable public contract of an Agent
without depending on Planner, Memory, Runtime or Kernel.

The public contract is:

    Agent.execute()     <- framework wrapper
            ↓
        Agent.run()     <- subclass implementation
"""

from __future__ import annotations

import pytest

from scios.agents.base import Agent


# ==========================================================
# Dummy Agent
# ==========================================================


class DummyAgent(Agent):
    """
    Minimal concrete implementation.
    """

    def run(self, task):
        return {
            "task": task,
            "status": "success",
        }


# ==========================================================
# Construction
# ==========================================================


def test_agent_construction() -> None:

    agent = DummyAgent(name="dummy")

    assert agent is not None
    assert isinstance(agent, Agent)


# ==========================================================
# Metadata
# ==========================================================


def test_agent_metadata() -> None:

    agent = DummyAgent(name="assistant")

    assert isinstance(agent.id, str)

    assert len(agent.id) > 10

    assert agent.name == "assistant"

    assert agent.version

    assert agent.enabled is True

    assert agent.state == "idle"


# ==========================================================
# Execute
# ==========================================================


def test_agent_execute() -> None:

    agent = DummyAgent(name="dummy")

    result = agent.execute("ping")

    assert result["status"] == "success"

    assert result["task"] == "ping"

    assert agent.state == "idle"


# ==========================================================
# Callable
# ==========================================================


def test_agent_callable() -> None:

    agent = DummyAgent(name="dummy")

    result = agent("hello")

    assert result["status"] == "success"

    assert result["task"] == "hello"


# ==========================================================
# Multiple Executions
# ==========================================================


def test_agent_multiple_execution() -> None:

    agent = DummyAgent(name="dummy")

    for i in range(20):

        result = agent.execute(f"task-{i}")

        assert result["status"] == "success"

    status = agent.status()

    assert status["executions"] == 20


# ==========================================================
# Status
# ==========================================================


def test_agent_status() -> None:

    agent = DummyAgent(name="dummy")

    status = agent.status()

    assert isinstance(status, dict)

    required = {

        "id",

        "name",

        "state",

        "version",

        "enabled",

        "executions",

        "created_at",

    }

    assert required.issubset(status.keys())

    assert status["state"] == "idle"


# ==========================================================
# Reset
# ==========================================================


def test_agent_reset() -> None:

    agent = DummyAgent(name="dummy")

    agent.execute("task")

    assert agent.status()["executions"] == 1

    agent.reset()

    status = agent.status()

    assert status["executions"] == 0

    assert status["state"] == "idle"


# ==========================================================
# Enable / Disable
# ==========================================================


def test_disable_agent() -> None:

    agent = DummyAgent(name="dummy")

    agent.disable()

    assert agent.enabled is False

    with pytest.raises(RuntimeError):

        agent.execute("task")


def test_enable_agent() -> None:

    agent = DummyAgent(name="dummy")

    agent.disable()

    agent.enable()

    result = agent.execute("task")

    assert result["status"] == "success"


# ==========================================================
# Invalid Task
# ==========================================================


def test_invalid_task() -> None:

    agent = DummyAgent(name="dummy")

    with pytest.raises(ValueError):

        agent.execute(None)


# ==========================================================
# Unique IDs
# ==========================================================


def test_unique_agent_ids() -> None:

    a = DummyAgent(name="a")

    b = DummyAgent(name="b")

    assert a.id != b.id


# ==========================================================
# Representation
# ==========================================================


def test_agent_repr() -> None:

    agent = DummyAgent(name="assistant")

    text = repr(agent)

    assert "assistant" in text

    assert "Agent" in text

    assert agent.id in text


# ==========================================================
# Execution Counter
# ==========================================================


def test_execution_counter() -> None:

    agent = DummyAgent(name="dummy")

    for _ in range(5):

        agent.execute("ping")

    assert agent.status()["executions"] == 5


# ==========================================================
# State Transition
# ==========================================================


def test_state_after_execution() -> None:

    agent = DummyAgent(name="dummy")

    assert agent.state == "idle"

    agent.execute("task")

    assert agent.state == "idle"


# ==========================================================
# Status Stability
# ==========================================================


def test_status_is_copy() -> None:

    agent = DummyAgent(name="dummy")

    status = agent.status()

    status["state"] = "corrupted"

    assert agent.status()["state"] == "idle"