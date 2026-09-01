"""Integration contract tests for the runtime Agent boundary.

These tests verify composition between:
    Agent ↔ Memory ↔ ToolRouter

The tests intentionally exercise public contracts rather than private
implementation details.
"""

from __future__ import annotations

from typing import Any

from scios.agents.base import Agent
from scios.runtime.agent.memory import Memory
from scios.runtime.agent.tool_router import ToolRouter


class IntegrationAgent(Agent):
    """Minimal concrete Agent used to verify the base Agent contract."""

    def run(
        self,
        task: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return {
            "ok": True,
            "task": task,
            "args": args,
            "kwargs": kwargs,
        }


def make_agent() -> tuple[IntegrationAgent, Memory, ToolRouter]:
    """Create a fully composed Agent for integration tests."""
    memory = Memory()
    router = ToolRouter()

    agent = IntegrationAgent(
        name="integration-test",
        memory=memory,
        router=router,
    )

    return agent, memory, router


class TestAgentDependencyInjection:
    """Verify Agent dependency composition."""

    def test_memory_is_injected_by_identity(self) -> None:
        agent, memory, _ = make_agent()

        assert agent.memory is memory

    def test_router_is_injected_by_identity(self) -> None:
        agent, _, router = make_agent()

        assert agent.router is router

    def test_tool_router_aliases_injected_router(self) -> None:
        agent, _, router = make_agent()

        assert agent.tool_router is router

    def test_router_and_tool_router_share_same_instance(self) -> None:
        agent, _, _ = make_agent()

        assert agent.router is agent.tool_router


class TestAgentMemoryIntegration:
    """Verify Agent ↔ Memory delegation."""

    def test_remember_writes_to_injected_memory(self) -> None:
        agent, memory, _ = make_agent()

        agent.remember("answer", 42)

        assert memory.get("answer") == 42

    def test_recall_reads_from_injected_memory(self) -> None:
        agent, memory, _ = make_agent()

        memory.store("answer", 42)

        assert agent.recall("answer") == 42

    def test_remember_and_recall_round_trip(self) -> None:
        agent, memory, _ = make_agent()

        agent.remember("answer", 42)

        assert agent.recall("answer") == 42
        assert memory.get("answer") == 42
        assert agent.recall("answer") == memory.get("answer")

    def test_recall_missing_key_returns_default(self) -> None:
        agent, _, _ = make_agent()

        assert agent.recall("missing", "fallback") == "fallback"


class TestAgentExecutionIntegration:
    """Verify Agent.execute() delegates to the concrete run() contract."""

    def test_execute_delegates_to_run(self) -> None:
        agent, _, _ = make_agent()

        result = agent.execute("hello")

        assert result == {
            "ok": True,
            "task": "hello",
            "args": (),
            "kwargs": {},
        }

    def test_execute_forwards_positional_arguments(self) -> None:
        agent, _, _ = make_agent()

        result = agent.execute("hello", 1, 2)

        assert result["task"] == "hello"
        assert result["args"] == (1, 2)

    def test_execute_forwards_keyword_arguments(self) -> None:
        agent, _, _ = make_agent()

        result = agent.execute("hello", mode="test", limit=3)

        assert result["task"] == "hello"
        assert result["kwargs"] == {
            "mode": "test",
            "limit": 3,
        }

    def test_execute_increments_execution_count(self) -> None:
        agent, _, _ = make_agent()

        before = agent.status()["executions"]

        agent.execute("hello")

        after = agent.status()["executions"]

        assert after == before + 1

    def test_execute_returns_agent_to_idle_state(self) -> None:
        agent, _, _ = make_agent()

        agent.execute("hello")

        status = agent.status()

        assert status["state"] == "idle"
        assert status["enabled"] is True


class TestAgentRuntimeIntegration:
    """Verify the combined Agent runtime contract."""

    def test_memory_and_execution_work_together(self) -> None:
        agent, memory, _ = make_agent()

        agent.remember("input", "hello")

        result = agent.execute(agent.recall("input"))

        assert result["ok"] is True
        assert result["task"] == "hello"
        assert memory.get("input") == "hello"

    def test_status_contains_runtime_identity(self) -> None:
        agent, _, _ = make_agent()

        status = agent.status()

        assert status["name"] == "integration-test"
        assert status["version"] == "0.3.0"
        assert status["enabled"] is True
        assert status["state"] == "idle"
        assert "id" in status
        assert "created_at" in status

    def test_multiple_executions_preserve_runtime_contract(self) -> None:
        agent, _, _ = make_agent()

        agent.execute("one")
        agent.execute("two")
        agent.execute("three")

        status = agent.status()

        assert status["executions"] == 3
        assert status["state"] == "idle"
        assert status["enabled"] is True