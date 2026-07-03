"""
SciOS Agent Tests
=================

Unit tests for the SciOS Agent abstraction.

These tests validate the stable public contract of an Agent without
depending on planners, memory systems, reasoning engines, or tools.
"""

from __future__ import annotations

import pytest

from scios.agents.base import Agent


# ==========================================================
# Dummy Agent
# ==========================================================

class DummyAgent(Agent):
    """
    Minimal concrete implementation used for testing.
    """

    def execute(self, task):
        return {
            "task": task,
            "status": "success",
        }


# ==========================================================
# Construction
# ==========================================================

def test_agent_construction() -> None:
    """
    Agent should be constructible.
    """

    agent = DummyAgent(name="dummy")

    assert agent is not None
    assert agent.name == "dummy"


# ==========================================================
# Metadata
# ==========================================================

def test_agent_metadata() -> None:
    """
    Agent metadata should be available.
    """

    agent = DummyAgent(name="assistant")

    assert agent.name == "assistant"
    assert isinstance(agent.id, str)


# ==========================================================
# Execute
# ==========================================================

def test_agent_execute() -> None:
    """
    Agent should execute a simple task.
    """

    agent = DummyAgent(name="dummy")

    result = agent.execute("ping")

    assert result["status"] == "success"
    assert result["task"] == "ping"


# ==========================================================
# Callable Interface
# ==========================================================

def test_agent_callable() -> None:
    """
    Agent should support __call__().
    """

    agent = DummyAgent(name="dummy")

    result = agent("hello")

    assert result["status"] == "success"


# ==========================================================
# Multiple Executions
# ==========================================================

def test_agent_multiple_execution() -> None:
    """
    Agent should execute multiple tasks.
    """

    agent = DummyAgent(name="dummy")

    for i in range(20):

        result = agent.execute(f"task-{i}")

        assert result["status"] == "success"


# ==========================================================
# Status
# ==========================================================

def test_agent_status() -> None:
    """
    Agent should expose a stable status schema.
    """

    agent = DummyAgent(name="dummy")

    status = agent.status()

    assert isinstance(status, dict)

    required = {
        "id",
        "name",
        "state",
    }

    assert required.issubset(status.keys())


# ==========================================================
# Reset
# ==========================================================

def test_agent_reset() -> None:
    """
    Reset should restore the initial state.
    """

    agent = DummyAgent(name="dummy")

    agent.execute("task")

    agent.reset()

    assert agent.status()["state"] == "idle"


# ==========================================================
# Representation
# ==========================================================

def test_agent_repr() -> None:
    """
    repr() should contain the agent name.
    """

    agent = DummyAgent(name="assistant")

    text = repr(agent)

    assert "assistant" in text


# ==========================================================
# Invalid Task
# ==========================================================

def test_invalid_task() -> None:
    """
    Invalid tasks should raise an exception.
    """

    agent = DummyAgent(name="dummy")

    with pytest.raises(Exception):

        agent.execute(None)


# ==========================================================
# Unique IDs
# ==========================================================

def test_unique_agent_ids() -> None:
    """
    Every agent should have a unique identifier.
    """

    a = DummyAgent(name="a")
    b = DummyAgent(name="b")

    assert a.id != b.id