"""
SciOS Runtime Agent Contract Tests
==================================

Contract tests for the Runtime Agent orchestration layer.

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.agent.agent import Agent
from scios.runtime.agent.state import AgentState
from scios.runtime.agent.memory import Memory
from scios.runtime.agent.planner import Planner
from scios.runtime.agent.tool_router import ToolRouter
from scios.runtime.tools.result import ToolResult


# ==========================================================
# Test Doubles
# ==========================================================


class RecordingPlanner(Planner):

    def __init__(
        self,
        plan_result=None,
    ) -> None:

        self.calls: list[str] = []
        self.plan_result = plan_result

    def create_plan(
        self,
        goal: str,
    ):

        self.calls.append(goal)

        if self.plan_result is not None:
            return self.plan_result

        return super().create_plan(goal)


class RecordingMemory(Memory):

    def __init__(self) -> None:

        super().__init__()

        self.store_calls: list[tuple[str, object]] = []
        self.get_calls: list[str] = []

    def store(
        self,
        key: str,
        value,
    ) -> None:

        self.store_calls.append(
            (key, value)
        )

        return super().store(
            key,
            value,
        )

    def get(
        self,
        key: str,
        default=None,
    ):

        self.get_calls.append(key)

        return super().get(
            key,
            default,
        )


class RecordingRouter(ToolRouter):

    def __init__(self) -> None:

        super().__init__()

        self.route_calls: list[
            tuple[str, dict]
        ] = []

    def route(
        self,
        name: str,
        **kwargs,
    ):

        self.route_calls.append(
            (name, kwargs)
        )

        return ToolResult.ok(
            {
                "tool": name,
                "args": kwargs,
            }
        )


class FailingPlanner(Planner):

    def create_plan(
        self,
        goal: str,
    ):

        raise RuntimeError(
            "planner failure"
        )


# ==========================================================
# Construction
# ==========================================================


def test_agent_creation():

    agent = Agent(
        name="test-agent"
    )

    assert agent.name == "test-agent"
    assert agent.runs == 0


def test_agent_default_name():

    agent = Agent()

    assert agent.name == "default-agent"


def test_agent_default_dependencies():

    agent = Agent()

    assert isinstance(
        agent.planner,
        Planner,
    )

    assert isinstance(
        agent.memory,
        Memory,
    )

    assert isinstance(
        agent.router,
        ToolRouter,
    )

    assert isinstance(
        agent.state,
        AgentState,
    )


# ==========================================================
# Dependency Injection
# ==========================================================


def test_agent_preserves_injected_planner():

    planner = Planner()

    agent = Agent(
        planner=planner,
    )

    assert agent.planner is planner


def test_agent_preserves_injected_memory():

    memory = Memory()

    agent = Agent(
        memory=memory,
    )

    assert agent.memory is memory


def test_agent_preserves_injected_router():

    router = ToolRouter()

    agent = Agent(
        router=router,
    )

    assert agent.router is router
    assert agent.tool_router is router


def test_agent_preserves_injected_state():

    state = AgentState()

    agent = Agent(
        state=state,
    )

    assert agent.state is state


# ==========================================================
# Planning
# ==========================================================


def test_agent_plan_delegates_to_planner():

    planner = RecordingPlanner()

    agent = Agent(
        planner=planner,
    )

    result = agent.plan(
        "build tool"
    )

    assert result == [
        "build tool"
    ]

    assert planner.calls == [
        "build tool"
    ]


# ==========================================================
# Memory
# ==========================================================


def test_agent_remember_delegates_to_memory():

    memory = RecordingMemory()

    agent = Agent(
        memory=memory,
    )

    agent.remember(
        "key",
        "value",
    )

    assert memory.store_calls == [
        ("key", "value")
    ]


def test_agent_recall_delegates_to_memory():

    memory = RecordingMemory()

    memory.store(
        "key",
        "value",
    )

    agent = Agent(
        memory=memory,
    )

    result = agent.recall(
        "key"
    )

    assert result == "value"
    assert memory.get_calls == [
        "key"
    ]


# ==========================================================
# Tool Routing
# ==========================================================


def test_agent_execute_tool_delegates_to_router():

    router = RecordingRouter()

    agent = Agent(
        router=router,
    )

    result = agent.execute_tool(
        "echo",
        text="hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True

    assert router.route_calls == [
        (
            "echo",
            {
                "text": "hello",
            },
        )
    ]


def test_agent_tool_router_alias():

    router = ToolRouter()

    agent = Agent(
        router=router,
    )

    assert agent.router is agent.tool_router


# ==========================================================
# Run Contract
# ==========================================================


def test_agent_run_response_contract():

    agent = Agent()

    result = agent.run(
        "hello",
    )

    assert isinstance(
        result,
        dict,
    )

    assert {
        "agent",
        "task",
        "plan",
        "result",
        "status",
    }.issubset(
        result.keys()
    )


def test_agent_run_success_contract():

    agent = Agent()

    result = agent.run(
        "hello",
    )

    assert result["agent"] == (
        "default-agent"
    )

    assert result["task"] == "hello"

    assert result["plan"] == [
        "hello"
    ]

    assert result["status"] == (
        "completed"
    )


def test_agent_run_increments_runs():

    agent = Agent()

    assert agent.runs == 0

    agent.run("task-1")

    assert agent.runs == 1

    agent.run("task-2")

    assert agent.runs == 2


# ==========================================================
# Run Lifecycle
# ==========================================================


def test_agent_run_updates_state_to_completed():

    agent = Agent()

    result = agent.run(
        "hello"
    )

    assert result["status"] == (
        "completed"
    )

    assert agent.state.status == (
        "completed"
    )

    assert agent.state.task == (
        "hello"
    )


def test_agent_run_stores_last_task():

    agent = Agent()

    agent.run(
        "hello"
    )

    assert agent.recall(
        "last_task"
    ) == "hello"


# ==========================================================
# Explicit Tool Execution
# ==========================================================


def test_agent_run_with_tool():

    router = RecordingRouter()

    agent = Agent(
        router=router,
    )

    result = agent.run(
        "hello",
        tool="echo",
        text="world",
    )

    assert result["status"] == (
        "completed"
    )

    assert router.route_calls == [
        (
            "echo",
            {
                "text": "world",
            },
        )
    ]


def test_agent_run_normalizes_tool_result():

    router = RecordingRouter()

    agent = Agent(
        router=router,
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
# Failure Contract
# ==========================================================


def test_agent_planner_failure_returns_failed_result():

    agent = Agent(
        planner=FailingPlanner(),
    )

    result = agent.run(
        "hello"
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["status"] == (
        "failed"
    )

    assert result["agent"] == (
        "default-agent"
    )

    assert result["task"] == "hello"

    assert result["plan"] is None

    assert result["result"] is None

    assert result["error"] == (
        "planner failure"
    )


def test_agent_planner_failure_updates_state():

    agent = Agent(
        planner=FailingPlanner(),
    )

    agent.run(
        "hello"
    )

    assert agent.state.status == (
        "failed"
    )

    assert agent.state.task == (
        "hello"
    )

    assert agent.state.error == (
        "planner failure"
    )


def test_agent_failure_increments_failed_counter():

    agent = Agent(
        planner=FailingPlanner(),
    )

    agent.run(
        "hello"
    )

    status = agent.status()

    assert status["runs"] == 1
    assert status["failed"] == 1
    assert status["success"] == 0


def test_agent_success_increments_success_counter():

    agent = Agent()

    agent.run(
        "hello"
    )

    status = agent.status()

    assert status["runs"] == 1
    assert status["success"] == 1
    assert status["failed"] == 0


# ==========================================================
# Status
# ==========================================================


def test_agent_status_contract():

    agent = Agent(
        name="status-agent"
    )

    status = agent.status()

    assert status["name"] == (
        "status-agent"
    )

    assert status["runs"] == 0
    assert status["success"] == 0
    assert status["failed"] == 0

    assert "state" in status
    assert "memory" in status
    assert "tools" in status


# ==========================================================
# Reset
# ==========================================================


def test_agent_reset_resets_state():

    agent = Agent()

    agent.run(
        "hello"
    )

    agent.reset()

    assert agent.state.status == (
        "idle"
    )

    assert agent.state.task is None
    assert agent.state.error is None
    assert agent.state.result is None


def test_agent_reset_does_not_reset_run_counter():

    agent = Agent()

    agent.run(
        "hello"
    )

    agent.reset()

    assert agent.runs == 1


# ==========================================================
# Callable
# ==========================================================


def test_agent_callable_delegates_to_run():

    agent = Agent()

    result = agent(
        "callable-task"
    )

    assert result["task"] == (
        "callable-task"
    )

    assert result["status"] == (
        "completed"
    )