"""
Agent ? ToolRouter ? ToolRegistry ? ToolExecutor ? ToolResult
end-to-end integration contracts.

This file intentionally tests only the Agent-to-tool boundary.
Lower-level ToolRouter, ToolRegistry, and ToolExecutor behavior
is covered by their dedicated contract suites.
"""

from scios.agents.base import Agent
from scios.runtime.agent.tool_router import ToolRouter
from scios.runtime.tools import (
    Tool,
    ToolExecutor,
    ToolRegistry,
    ToolResult,
)


# ==========================================================
# Test Agent
# ==========================================================


class IntegrationAgent(Agent):

    def run(self, task, *args, **kwargs):
        return {
            "task": task,
            "args": args,
            "kwargs": kwargs,
        }


# ==========================================================
# Test Tools
# ==========================================================


class EchoTool(Tool):

    NAME = "echo"
    DESCRIPTION = "Echo value"
    VERSION = "1.0.0"

    def execute(self, value):
        return value


class AddTool(Tool):

    NAME = "add"
    DESCRIPTION = "Add two values"

    def execute(self, a, b):
        return a + b


class FailingTool(Tool):

    NAME = "failing"
    DESCRIPTION = "Always fails"

    def execute(self):
        raise RuntimeError("tool failed")


# ==========================================================
# Construction / Dependency Identity
# ==========================================================


def test_agent_preserves_injected_tool_router():

    router = ToolRouter()

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    assert agent.router is router
    assert agent.tool_router is router


def test_agent_tool_router_has_runtime_dependencies():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    assert agent.tool_router is router
    assert agent.tool_router.registry is registry
    assert agent.tool_router.executor is executor
    assert agent.tool_router.executor.registry is registry


# ==========================================================
# Agent ? Router ? Registry ? Executor ? Result
# ==========================================================


def test_agent_execute_tool_end_to_end():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    tool = EchoTool()

    agent.tool_router.register(
        tool,
    )

    result = agent.execute_tool(
        "echo",
        value="hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"

    assert registry.get(
        "echo",
    ) is tool

    assert router.executions == 1
    assert executor.executions == 1
    assert executor.success == 1
    assert executor.failed == 0


def test_agent_execute_tool_preserves_arguments():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    router.register(
        AddTool(),
    )

    result = agent.execute_tool(
        "add",
        a=20,
        b=22,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == 42


# ==========================================================
# Multiple Tools
# ==========================================================


def test_agent_can_execute_multiple_registered_tools():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    router.register(
        EchoTool(),
    )

    router.register(
        AddTool(),
    )

    echo = agent.execute_tool(
        "echo",
        value="scios",
    )

    add = agent.execute_tool(
        "add",
        a=10,
        b=32,
    )

    assert echo.success is True
    assert echo.value == "scios"

    assert add.success is True
    assert add.value == 42

    assert router.executions == 2
    assert executor.executions == 2
    assert executor.success == 2
    assert executor.failed == 0


# ==========================================================
# Unknown Tool
# ==========================================================


def test_agent_execute_tool_unknown_tool():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    result = agent.execute_tool(
        "missing",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        ValueError,
    )

    assert str(result.error) == (
        "Tool not found: missing"
    )

    assert router.executions == 1

    # Router rejects the request before Executor receives it.
    assert executor.executions == 0
    assert executor.success == 0
    assert executor.failed == 0


# ==========================================================
# Tool Execution Failure
# ==========================================================


def test_agent_execute_tool_propagates_tool_failure():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    router.register(
        FailingTool(),
    )

    result = agent.execute_tool(
        "failing",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        RuntimeError,
    )

    assert str(result.error) == (
        "tool failed"
    )

    assert router.executions == 1
    assert executor.executions == 1
    assert executor.success == 0
    assert executor.failed == 1


# ==========================================================
# Mixed End-to-End Execution
# ==========================================================


def test_agent_mixed_tool_execution_preserves_boundaries():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    router.register(
        EchoTool(),
    )

    success_one = agent.execute_tool(
        "echo",
        value="one",
    )

    missing = agent.execute_tool(
        "missing",
    )

    success_two = agent.execute_tool(
        "echo",
        value="two",
    )

    assert success_one.success is True
    assert success_one.value == "one"

    assert missing.success is False
    assert isinstance(
        missing.error,
        ValueError,
    )

    assert success_two.success is True
    assert success_two.value == "two"

    # Agent-facing routing sees all three requests.
    assert router.executions == 3

    # Executor sees only the two requests that reached it.
    assert executor.executions == 2
    assert executor.success == 2
    assert executor.failed == 0


# ==========================================================
# Agent Execution vs Tool Execution
# ==========================================================


def test_agent_execute_tool_does_not_increment_agent_run_count():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    router.register(
        EchoTool(),
    )

    assert agent.executions == 0

    result = agent.execute_tool(
        "echo",
        value="hello",
    )

    assert result.success is True

    # execute_tool belongs to the tool boundary,
    # not Agent.run()/Agent.execute() lifecycle.
    assert agent.executions == 0

    assert router.executions == 1
    assert executor.executions == 1


# ==========================================================
# Identity Invariant
# ==========================================================


def test_end_to_end_dependency_identity():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    agent = IntegrationAgent(
        name="integration-agent",
        router=router,
    )

    tool = EchoTool()

    agent.tool_router.register(
        tool,
    )

    assert agent.tool_router is router
    assert router.registry is registry
    assert router.executor is executor
    assert executor.registry is registry

    assert registry.get(
        "echo",
    ) is tool

    assert router.resolve(
        "echo",
    ) is tool

    result = agent.execute_tool(
        "echo",
        value="contract",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "contract"
