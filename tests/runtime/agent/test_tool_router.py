"""
SciOS Runtime Agent ToolRouter Tests
====================================

Comprehensive contract tests for ToolRouter.

Architecture:

    Agent
      |
    ToolRouter
      |
    ToolExecutor
      |
    ToolSandbox
      |
    Tool
      |
    ToolResult

Python 3.11+
"""

from __future__ import annotations


import pytest


from scios.runtime.agent.tool_router import (
    ToolRouter,
)

from scios.runtime.tools import (
    Tool,
    ToolExecutor,
    ToolPolicy,
    ToolRegistry,
    ToolResult,
    ToolSandbox,
)


# ==========================================================
# Mock Tools
# ==========================================================


class EchoTool(Tool):
    """Return the supplied text."""

    NAME = "echo"

    DESCRIPTION = "Return input text"

    VERSION = "1.0.0"

    def execute(
        self,
        text: str,
    ) -> ToolResult:

        return ToolResult.ok(
            text
        )


class AddTool(Tool):
    """Add two numbers."""

    NAME = "add"

    DESCRIPTION = "Add two numbers"

    VERSION = "1.0.0"

    def execute(
        self,
        a: int,
        b: int,
    ) -> int:

        return a + b


class FailingTool(Tool):
    """Tool that always raises."""

    NAME = "failing"

    def execute(self) -> None:

        raise RuntimeError(
            "tool failed"
        )


# ==========================================================
# Construction
# ==========================================================


def test_router_default_construction():

    router = ToolRouter()

    assert isinstance(
        router.registry,
        ToolRegistry,
    )

    assert isinstance(
        router.executor,
        ToolExecutor,
    )

    assert router.executions == 0


def test_router_custom_registry():

    registry = ToolRegistry()

    router = ToolRouter(
        registry=registry,
    )

    assert router.registry is registry


def test_router_custom_executor():

    executor = ToolExecutor()

    router = ToolRouter(
        executor=executor,
    )

    assert router.executor is executor


def test_router_preserves_custom_components():

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


# ==========================================================
# Registration
# ==========================================================


def test_router_register():

    router = ToolRouter()

    tool = EchoTool()

    returned = router.register(
        tool
    )

    assert returned is tool
    assert router.registry.get(
        "echo"
    ) is tool


def test_router_register_multiple_tools():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    router.register(
        AddTool()
    )

    assert router.list_tools() == [
        "echo",
        "add",
    ]

    assert len(router) == 2


def test_router_has_tool():

    router = ToolRouter()

    assert router.has_tool(
        "echo"
    ) is False

    router.register(
        EchoTool()
    )

    assert router.has_tool(
        "echo"
    ) is True


def test_router_contains():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    assert "echo" in router
    assert "missing" not in router


# ==========================================================
# Resolve
# ==========================================================


def test_router_resolve():

    router = ToolRouter()

    tool = EchoTool()

    router.register(
        tool
    )

    resolved = router.resolve(
        "echo"
    )

    assert resolved is tool


def test_router_resolve_missing():

    router = ToolRouter()

    with pytest.raises(
        ValueError,
        match="Tool not found: unknown",
    ):

        router.resolve(
            "unknown"
        )


# ==========================================================
# Unregister
# ==========================================================


def test_router_unregister():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    removed = router.unregister(
        "echo"
    )

    assert removed is not None
    assert router.has_tool(
        "echo"
    ) is False


def test_router_unregister_missing():

    router = ToolRouter()

    removed = router.unregister(
        "unknown"
    )

    assert removed is None


# ==========================================================
# Route Execution
# ==========================================================


def test_router_route_toolresult():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    result = router.route(
        "echo",
        text="hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"


def test_router_route_raw_value():

    router = ToolRouter()

    router.register(
        AddTool()
    )

    result = router.route(
        "add",
        a=2,
        b=3,
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == 5


def test_router_route_increments_executions():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    assert router.executions == 0

    router.route(
        "echo",
        text="one",
    )

    assert router.executions == 1

    router.route(
        "echo",
        text="two",
    )

    assert router.executions == 2


# ==========================================================
# Route Errors
# ==========================================================


def test_router_route_missing_tool():

    router = ToolRouter()

    result = router.route(
        "unknown",
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

    assert result.message == (
        "Tool not found: unknown"
    )


def test_router_route_failing_tool():

    router = ToolRouter()

    router.register(
        FailingTool()
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

    assert result.message == (
        "tool failed"
    )


def test_router_route_error_increments_executions():

    router = ToolRouter()

    result = router.route(
        "missing",
    )

    assert result.success is False
    assert router.executions == 1


# ==========================================================
# Callable API
# ==========================================================


def test_router_callable():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    result = router(
        "echo",
        text="scios",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "scios"


def test_router_callable_matches_route():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    direct = router.route(
        "echo",
        text="hello",
    )

    callable_result = router(
        "echo",
        text="world",
    )

    assert direct.value == "hello"
    assert callable_result.value == "world"


# ==========================================================
# Batch Execution
# ==========================================================


def test_router_route_many():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    results = router.route_many(
        [
            {
                "name": "echo",
                "args": {
                    "text": "one",
                },
            },
            {
                "name": "echo",
                "args": {
                    "text": "two",
                },
            },
            {
                "name": "echo",
                "args": {
                    "text": "three",
                },
            },
        ]
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
        "one",
        "two",
        "three",
    ]


def test_router_route_many_mixed_results():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    results = router.route_many(
        [
            {
                "name": "echo",
                "args": {
                    "text": "ok",
                },
            },
            {
                "name": "unknown",
                "args": {},
            },
        ]
    )

    assert len(results) == 2

    assert results[0].success is True
    assert results[0].value == "ok"

    assert results[1].success is False


def test_router_route_many_missing_name():

    router = ToolRouter()

    results = router.route_many(
        [
            {
                "args": {
                    "text": "hello",
                },
            }
        ]
    )

    assert len(results) == 1

    result = results[0]

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        ValueError,
    )

    assert result.message == (
        "Missing tool name"
    )


def test_router_route_many_increments_executions():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    router.route_many(
        [
            {
                "name": "echo",
                "args": {
                    "text": "one",
                },
            },
            {
                "name": "echo",
                "args": {
                    "text": "two",
                },
            },
        ]
    )

    assert router.executions == 2


# ==========================================================
# Diagnostics
# ==========================================================


def test_router_status_empty():

    router = ToolRouter()

    status = router.status()

    assert status["count"] == 0
    assert status["tools"] == []
    assert status["executions"] == 0


def test_router_status():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    router.route(
        "echo",
        text="hello",
    )

    status = router.status()

    assert status["count"] == 1
    assert status["tools"] == [
        "echo",
    ]
    assert status["executions"] == 1


# ==========================================================
# Protocol
# ==========================================================


def test_router_len():

    router = ToolRouter()

    assert len(router) == 0

    router.register(
        EchoTool()
    )

    assert len(router) == 1

    router.register(
        AddTool()
    )

    assert len(router) == 2


def test_router_repr():

    router = ToolRouter()

    representation = repr(
        router
    )

    assert representation.startswith(
        "ToolRouter("
    )

    assert "tools=0" in representation
    assert "executions=0" in representation


def test_router_repr_after_execution():

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    router.route(
        "echo",
        text="hello",
    )

    representation = repr(
        router
    )

    assert "tools=1" in representation
    assert "executions=1" in representation


# ==========================================================
# Integration
# ==========================================================


def test_router_uses_registered_tool():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    executor = ToolExecutor(
        registry=registry,
    )

    router = ToolRouter(
        registry=registry,
        executor=executor,
    )

    result = router.route(
        "echo",
        text="integration",
    )

    assert result.success is True
    assert result.value == "integration"


def test_router_shared_registry():

    registry = ToolRegistry()

    router = ToolRouter(
        registry=registry,
    )

    tool = EchoTool()

    registry.register(
        tool
    )

    assert router.has_tool(
        "echo"
    )

    assert router.resolve(
        "echo"
    ) is tool


# ==========================================================
# Contract Summary
# ==========================================================


def test_router_public_contract():

    router = ToolRouter()

    assert hasattr(
        router,
        "registry",
    )

    assert hasattr(
        router,
        "executor",
    )

    assert hasattr(
        router,
        "executions",
    )

    assert callable(
        router.register
    )

    assert callable(
        router.unregister
    )

    assert callable(
        router.resolve
    )

    assert callable(
        router.route
    )

    assert callable(
        router.route_many
    )

    assert callable(
        router.list_tools
    )

    assert callable(
        router.has_tool
    )

    assert callable(
        router.status
    )

    assert callable(
        router
    )