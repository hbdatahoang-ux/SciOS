"""
ToolRouter ? ToolRegistry ? ToolExecutor integration contracts.

These tests verify the real runtime composition boundary:

    ToolRouter
        ?
    ToolRegistry
        ?
       Tool
        ?
    ToolExecutor
        ?
    ToolResult

The tests intentionally use the public runtime APIs only.
"""

import pytest

from scios.runtime.agent.tool_router import ToolRouter
from scios.runtime.tools import (
    Tool,
    ToolExecutor,
    ToolRegistry,
    ToolResult,
)


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
    DESCRIPTION = "Add two numbers"

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


def test_router_owns_runtime_registry_and_executor():

    router = ToolRouter()

    assert isinstance(
        router.registry,
        ToolRegistry,
    )

    assert isinstance(
        router.executor,
        ToolExecutor,
    )


def test_router_preserves_injected_registry():

    registry = ToolRegistry()

    router = ToolRouter(
        registry=registry,
    )

    assert router.registry is registry


def test_router_preserves_injected_executor():

    executor = ToolExecutor()

    router = ToolRouter(
        executor=executor,
    )

    assert router.executor is executor


def test_router_preserves_shared_dependencies():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    assert router.registry is registry
    assert router.executor is executor
    assert router.executor.registry is registry


# ==========================================================
# Registration ? Registry ? Router
# ==========================================================


def test_router_registers_into_registry():

    registry = ToolRegistry()

    router = ToolRouter(
        registry=registry,
    )

    tool = EchoTool()

    returned = router.register(
        tool,
    )

    assert returned is tool

    assert registry.exists(
        "echo",
    )

    assert registry.get(
        "echo",
    ) is tool


def test_router_resolves_exact_registered_tool():

    registry = ToolRegistry()

    router = ToolRouter(
        registry=registry,
    )

    tool = EchoTool()

    router.register(
        tool,
    )

    assert router.resolve(
        "echo",
    ) is tool

    assert registry.get(
        "echo",
    ) is tool


def test_registry_mutation_is_visible_to_router():

    registry = ToolRegistry()

    router = ToolRouter(
        registry=registry,
    )

    tool = EchoTool()

    registry.register(
        tool,
    )

    assert router.has_tool(
        "echo",
    )

    assert router.resolve(
        "echo",
    ) is tool

    assert router.list_tools() == [
        "echo",
    ]


# ==========================================================
# Router ? Executor ? Tool
# ==========================================================


def test_route_executes_registered_tool_through_executor():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    result = router.route(
        "echo",
        value="integration",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "integration"

    assert router.executions == 1
    assert executor.executions == 1
    assert executor.success == 1
    assert executor.failed == 0


def test_route_selects_correct_registered_tool():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    router.register(
        AddTool(),
    )

    echo_result = router.route(
        "echo",
        value="hello",
    )

    add_result = router.route(
        "add",
        a=20,
        b=22,
    )

    assert echo_result.success is True
    assert echo_result.value == "hello"

    assert add_result.success is True
    assert add_result.value == 42

    assert router.executions == 2
    assert executor.executions == 2
    assert executor.success == 2


# ==========================================================
# Error Propagation
# ==========================================================


def test_unknown_tool_produces_tool_result_failure():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    result = router.route(
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
    assert executor.executions == 0
    assert executor.success == 0
    assert executor.failed == 0


def test_tool_failure_propagates_through_router():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        FailingTool(),
    )

    result = router.route(
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

    assert result.message == "tool failed"

    assert router.executions == 1
    assert executor.executions == 1
    assert executor.success == 0
    assert executor.failed == 1


# ==========================================================
# Shared State / Statistics
# ==========================================================


def test_router_and_executor_statistics_track_same_execution():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    router.route(
        "echo",
        value="one",
    )

    router.route(
        "echo",
        value="two",
    )

    assert router.executions == 2

    assert executor.executions == 2
    assert executor.success == 2
    assert executor.failed == 0


def test_router_and_executor_track_mixed_results():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    first = router.route(
        "echo",
        value="ok",
    )

    second = router.route(
        "missing",
    )

    third = router.route(
        "echo",
        value="again",
    )

    assert first.success is True
    assert second.success is False
    assert third.success is True

    assert router.executions == 3

    assert executor.executions == 2
    assert executor.success == 2
    assert executor.failed == 0

    assert router.executions == 3
    assert router.executions > executor.executions


# ==========================================================
# Unregister Boundary
# ==========================================================


def test_unregister_removes_tool_from_shared_registry():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    tool = EchoTool()

    router.register(
        tool,
    )

    assert router.has_tool(
        "echo",
    )

    removed = router.unregister(
        "echo",
    )

    assert removed is tool

    assert not registry.exists(
        "echo",
    )

    assert not router.has_tool(
        "echo",
    )

    assert router.list_tools() == []


def test_unregistered_tool_can_no_longer_execute():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    router.unregister(
        "echo",
    )

    result = router.route(
        "echo",
        value="should-fail",
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
        "Tool not found: echo"
    )


# ==========================================================
# Batch Integration
# ==========================================================


def test_route_many_preserves_registry_executor_pipeline():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    router.register(
        AddTool(),
    )

    results = router.route_many(
        [
            {
                "name": "echo",
                "args": {
                    "value": "first",
                },
            },
            {
                "name": "add",
                "args": {
                    "a": 10,
                    "b": 32,
                },
            },
            {
                "name": "echo",
                "args": {
                    "value": "third",
                },
            },
        ],
    )

    assert len(results) == 3

    assert all(
        isinstance(
            result,
            ToolResult,
        )
        for result in results
    )

    assert [
        result.value
        for result in results
    ] == [
        "first",
        42,
        "third",
    ]

    assert router.executions == 3

    assert executor.executions == 3
    assert executor.success == 3
    assert executor.failed == 0


def test_route_many_mixed_success_failure_preserves_pipeline():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    router.register(
        EchoTool(),
    )

    results = router.route_many(
        [
            {
                "name": "echo",
                "args": {
                    "value": "ok",
                },
            },
            {
                "name": "missing",
                "args": {},
            },
            {
                "name": "echo",
                "args": {
                    "value": "again",
                },
            },
        ],
    )

    assert len(results) == 3

    assert results[0].success is True
    assert results[0].value == "ok"

    assert results[1].success is False
    assert isinstance(
        results[1].error,
        ValueError,
    )

    assert str(results[1].error) == (
        "Tool not found: missing"
    )

    assert results[2].success is True
    assert results[2].value == "again"

    assert router.executions == 3

    assert executor.executions == 2
    assert executor.success == 2
    assert executor.failed == 0


# ==========================================================
# Contract Invariants
# ==========================================================


def test_router_registry_executor_contract():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    assert router.registry is registry
    assert router.executor is executor
    assert executor.registry is registry

    tool = EchoTool()

    router.register(
        tool,
    )

    assert router.has_tool("echo")
    assert registry.exists("echo")
    assert registry.get("echo") is tool
    assert router.resolve("echo") is tool

    result = router.route(
        "echo",
        value="contract",
    )

    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.value == "contract"

    assert router.executions == 1
    assert executor.executions == 1
    assert executor.success == 1
    assert executor.failed == 0


def test_router_does_not_replace_injected_dependencies():

    registry = ToolRegistry()

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    original_registry = router.registry
    original_executor = router.executor

    router.register(
        EchoTool(),
    )

    router.route(
        "echo",
        value="stable",
    )

    assert router.registry is original_registry
    assert router.executor is original_executor
    assert router.executor.registry is original_registry
