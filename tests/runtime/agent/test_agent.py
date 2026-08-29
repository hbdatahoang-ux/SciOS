"""
SciOS Runtime Agent Tests
=========================

Contract tests for the SciOS Runtime Agent.

Coverage
--------

- construction
- identity
- dependency injection
- validation
- planning
- memory delegation
- tool delegation
- run lifecycle
- ToolResult normalization
- planner/tool failures
- counters
- state reset
- shutdown
- status
- serialization
- callable interface
- representation

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.agent.agent import Agent
from scios.runtime.agent.memory import Memory
from scios.runtime.agent.planner import Planner
from scios.runtime.agent.state import AgentState
from scios.runtime.agent.tool_router import ToolRouter
from scios.runtime.tools.result import ToolResult


# ==========================================================
# Test Doubles
# ==========================================================


class RecordingPlanner(Planner):
    """Planner double recording planning requests."""

    def __init__(self):
        self.calls: list[str] = []

    def create_plan(self, goal):
        self.calls.append(goal)
        return {
            "goal": goal,
        }


class FailingPlanner(Planner):
    """Planner double that always fails."""

    def create_plan(self, goal):
        raise RuntimeError("planner failed")


class RecordingMemory(Memory):
    """Memory double recording operations."""

    def __init__(self):
        super().__init__()
        self.store_calls = []
        self.get_calls = []

    def store(self, key, value):
        self.store_calls.append((key, value))
        return super().store(key, value)

    def get(self, key, default=None):
        self.get_calls.append((key, default))
        return super().get(key, default)


class RecordingRouter(ToolRouter):
    """Router double recording tool executions."""

    def __init__(self):
        super().__init__()
        self.calls = []

    def route(self, name, **kwargs):
        self.calls.append((name, kwargs))
        return ToolResult.ok(
            {
                "tool": name,
                "args": kwargs,
            }
        )


class FailingRouter(ToolRouter):
    """Router double returning a failed ToolResult."""

    def route(self, name, **kwargs):
        return ToolResult.fail(
            RuntimeError("tool failed")
        )


class RecordingState(AgentState):
    """State double recording lifecycle operations."""

    def __init__(self):
        super().__init__()
        self.start_calls = []
        self.complete_calls = []
        self.fail_calls = []

    def start(self, task):
        self.start_calls.append(task)
        return super().start(task)

    def complete(self, result):
        self.complete_calls.append(result)
        return super().complete(result)

    def fail(self, error):
        self.fail_calls.append(error)
        return super().fail(error)


class RecordingRegistry:
    """Minimal registry double for shutdown testing."""

    def __init__(self):
        self.clear_calls = 0

    def clear(self):
        self.clear_calls += 1


class RouterWithRegistry(ToolRouter):
    """Router exposing a recording registry."""

    def __init__(self, registry):
        super().__init__()
        self._registry = registry


# ==========================================================
# Construction
# ==========================================================


def test_agent_creation():

    agent = Agent(
        name="test-agent"
    )

    assert agent.name == "test-agent"
    assert agent.runs == 0
    assert agent.success == 0
    assert agent.failed == 0


def test_agent_default_name():

    agent = Agent()

    assert agent.name == "default-agent"


def test_agent_rejects_non_string_name():

    with pytest.raises(TypeError):

        Agent(
            name=123
        )


def test_agent_rejects_empty_name():

    with pytest.raises(ValueError):

        Agent(
            name=""
        )


# ==========================================================
# Dependency Injection
# ==========================================================


def test_agent_preserves_injected_state():

    state = RecordingState()

    agent = Agent(
        state=state
    )

    assert agent.state is state


def test_agent_preserves_injected_memory():

    memory = RecordingMemory()

    agent = Agent(
        memory=memory
    )

    assert agent.memory is memory


def test_agent_preserves_injected_planner():

    planner = RecordingPlanner()

    agent = Agent(
        planner=planner
    )

    assert agent.planner is planner


def test_agent_preserves_injected_router():

    router = RecordingRouter()

    agent = Agent(
        router=router
    )

    assert agent.router is router
    assert agent.tool_router is router


def test_agent_creates_default_dependencies():

    agent = Agent()

    assert isinstance(
        agent.state,
        AgentState,
    )

    assert isinstance(
        agent.memory,
        Memory,
    )

    assert isinstance(
        agent.planner,
        Planner,
    )

    assert isinstance(
        agent.router,
        ToolRouter,
    )


# ==========================================================
# Planning
# ==========================================================


def test_agent_plan_delegates_to_planner():

    planner = RecordingPlanner()

    agent = Agent(
        planner=planner
    )

    result = agent.plan(
        "hello"
    )

    assert planner.calls == [
        "hello"
    ]

    assert result == {
        "goal": "hello"
    }


def test_agent_plan_rejects_non_string_task():

    agent = Agent()

    with pytest.raises(TypeError):

        agent.plan(
            123
        )


# ==========================================================
# Memory
# ==========================================================


def test_agent_remember_and_recall():

    agent = Agent()

    agent.remember(
        "key",
        "value",
    )

    assert agent.recall(
        "key"
    ) == "value"


def test_agent_recall_default():

    agent = Agent()

    assert agent.recall(
        "missing"
    ) is None


def test_agent_recall_custom_default():

    agent = Agent()

    assert agent.recall(
        "missing",
        "fallback",
    ) == "fallback"


def test_agent_memory_delegation():

    memory = RecordingMemory()

    agent = Agent(
        memory=memory
    )

    agent.remember(
        "key",
        "value",
    )

    result = agent.recall(
        "key",
        "default",
    )

    assert memory.store_calls == [
        ("key", "value")
    ]

    assert memory.get_calls == [
        ("key", "default")
    ]

    assert result == "value"


# ==========================================================
# Tool Delegation
# ==========================================================


def test_agent_execute_tool_delegates_to_router():

    router = RecordingRouter()

    agent = Agent(
        router=router
    )

    result = agent.execute_tool(
        "echo",
        text="hello",
    )

    assert router.calls == [
        (
            "echo",
            {
                "text": "hello",
            },
        )
    ]

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True


# ==========================================================
# Run — Basic Contract
# ==========================================================


def test_agent_run():

    agent = Agent(
        name="test-agent"
    )

    result = agent.run(
        "hello"
    )

    assert result is not None

    assert isinstance(
        result,
        dict,
    )


def test_agent_run_response_contract():

    agent = Agent(
        name="test-agent"
    )

    result = agent.run(
        "hello"
    )

    assert set(
        (
            "agent",
            "task",
            "plan",
            "result",
            "status",
        )
    ).issubset(
        result.keys()
    )


def test_agent_run_identity():

    agent = Agent(
        name="test-agent"
    )

    result = agent.run(
        "hello"
    )

    assert result["agent"] == "test-agent"
    assert result["task"] == "hello"


def test_agent_run_success_status():

    agent = Agent()

    result = agent.run(
        "hello"
    )

    assert result["status"] == "completed"


# ==========================================================
# Run — Planning
# ==========================================================


def test_agent_run_calls_planner():

    planner = RecordingPlanner()

    agent = Agent(
        planner=planner
    )

    result = agent.run(
        "hello"
    )

    assert planner.calls == [
        "hello"
    ]

    assert result["plan"] == {
        "goal": "hello"
    }


# ==========================================================
# Run — Memory
# ==========================================================


def test_agent_run_remembers_last_task():

    agent = Agent()

    agent.run(
        "hello"
    )

    assert agent.recall(
        "last_task"
    ) == "hello"


# ==========================================================
# Run — Explicit Tool
# ==========================================================


def test_agent_run_with_explicit_tool():

    router = RecordingRouter()

    agent = Agent(
        router=router
    )

    result = agent.run(
        "hello",
        tool="echo",
        text="world",
    )

    assert router.calls == [
        (
            "echo",
            {
                "text": "world",
            },
        )
    ]

    assert result["status"] == "completed"


def test_agent_run_normalizes_tool_result():

    router = RecordingRouter()

    agent = Agent(
        router=router
    )

    result = agent.run(
        "hello",
        tool="echo",
        text="world",
    )

    assert isinstance(
        result["result"],
        dict,
    )

    assert result["result"]["success"] is True


# ==========================================================
# Run — Tool Failure
# ==========================================================


def test_agent_run_failed_tool():

    router = FailingRouter()

    agent = Agent(
        router=router
    )

    result = agent.run(
        "hello",
        tool="broken",
    )

    assert result["status"] == "failed"


def test_agent_run_failed_tool_normalized():

    router = FailingRouter()

    agent = Agent(
        router=router
    )

    result = agent.run(
        "hello",
        tool="broken",
    )

    assert result["result"]["success"] is False


# ==========================================================
# Run — Plan Tool Execution
# ==========================================================


def test_agent_executes_tool_from_plan():

    class ToolPlanner(Planner):

        def create_plan(self, goal):

            return {
                "tool": "echo",
                "args": {
                    "text": "hello",
                },
            }

    router = RecordingRouter()

    agent = Agent(
        planner=ToolPlanner(),
        router=router,
    )

    result = agent.run(
        "hello"
    )

    assert router.calls == [
        (
            "echo",
            {
                "text": "hello",
            },
        )
    ]

    assert result["status"] == "completed"


def test_agent_returns_non_tool_plan_as_result():

    planner = RecordingPlanner()

    agent = Agent(
        planner=planner
    )

    result = agent.run(
        "hello"
    )

    assert result["result"] == {
        "goal": "hello"
    }


# ==========================================================
# Run — Planner Failure
# ==========================================================


def test_agent_planner_failure_is_contained():

    agent = Agent(
        planner=FailingPlanner()
    )

    result = agent.run(
        "hello"
    )

    assert result["status"] == "failed"

    assert result["task"] == "hello"

    assert result["result"] is None

    assert "error" in result

    assert "planner failed" in result["error"]


# ==========================================================
# State Lifecycle
# ==========================================================


def test_agent_run_starts_state():

    state = RecordingState()

    agent = Agent(
        state=state
    )

    agent.run(
        "hello"
    )

    assert state.start_calls == [
        "hello"
    ]


def test_agent_success_completes_state():

    state = RecordingState()

    agent = Agent(
        state=state
    )

    agent.run(
        "hello"
    )

    assert len(
        state.complete_calls
    ) == 1


def test_agent_failure_fails_state():

    state = RecordingState()

    agent = Agent(
        state=state,
        planner=FailingPlanner(),
    )

    agent.run(
        "hello"
    )

    assert len(
        state.fail_calls
    ) == 1


# ==========================================================
# Counters
# ==========================================================


def test_agent_initial_counters():

    agent = Agent()

    assert agent.runs == 0
    assert agent.success == 0
    assert agent.failed == 0


def test_agent_success_counter():

    agent = Agent()

    agent.run(
        "hello"
    )

    assert agent.runs == 1
    assert agent.success == 1
    assert agent.failed == 0


def test_agent_failure_counter():

    agent = Agent(
        planner=FailingPlanner()
    )

    agent.run(
        "hello"
    )

    assert agent.runs == 1
    assert agent.success == 0
    assert agent.failed == 1


def test_agent_multiple_runs():

    agent = Agent()

    agent.run("one")
    agent.run("two")

    assert agent.runs == 2
    assert agent.success == 2
    assert agent.failed == 0


# ==========================================================
# Reset
# ==========================================================


def test_agent_reset_resets_state():

    agent = Agent()

    agent.run(
        "hello"
    )

    agent.reset()

    assert agent.state.to_dict() is not None


def test_agent_reset_preserves_counters():

    agent = Agent()

    agent.run(
        "hello"
    )

    agent.reset()

    assert agent.runs == 1
    assert agent.success == 1
    assert agent.failed == 0


# ==========================================================
# Status
# ==========================================================


def test_agent_status():

    agent = Agent(
        name="test-agent"
    )

    status = agent.status()

    assert isinstance(
        status,
        dict,
    )

    assert status["name"] == "test-agent"


def test_agent_status_contains_diagnostics():

    agent = Agent()

    status = agent.status()

    assert "name" in status
    assert "runs" in status
    assert "success" in status
    assert "failed" in status
    assert "state" in status
    assert "memory" in status
    assert "tools" in status


def test_agent_status_updates_after_run():

    agent = Agent()

    agent.run(
        "hello"
    )

    status = agent.status()

    assert status["runs"] == 1
    assert status["success"] == 1
    assert status["failed"] == 0


# ==========================================================
# Serialization
# ==========================================================


def test_agent_to_dict():

    agent = Agent(
        name="test-agent"
    )

    data = agent.to_dict()

    assert isinstance(
        data,
        dict,
    )

    assert data["name"] == "test-agent"

    assert "status" in data


def test_agent_to_dict_after_run():

    agent = Agent(
        name="test-agent"
    )

    agent.run(
        "hello"
    )

    data = agent.to_dict()

    assert data["name"] == "test-agent"

    assert data["status"]["runs"] == 1


# ==========================================================
# Shutdown
# ==========================================================


def test_agent_shutdown_clears_router_registry():

    registry = RecordingRegistry()

    router = RouterWithRegistry(
        registry
    )

    agent = Agent(
        router=router
    )

    agent.shutdown()

    assert registry.clear_calls == 1


def test_agent_shutdown_preserves_router_identity():

    router = ToolRouter()

    agent = Agent(
        router=router
    )

    agent.shutdown()

    assert agent.router is router


# ==========================================================
# Callable Interface
# ==========================================================


def test_agent_callable():

    agent = Agent()

    result = agent(
        "callable-task"
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["task"] == (
        "callable-task"
    )

    assert result["status"] == (
        "completed"
    )


# ==========================================================
# Representation
# ==========================================================


def test_agent_repr():

    agent = Agent(
        name="test-agent"
    )

    representation = repr(
        agent
    )

    assert "Agent" in representation

    assert "test-agent" in representation

    assert "runs=0" in representation