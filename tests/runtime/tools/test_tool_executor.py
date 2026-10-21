"""
ToolExecutor tests
==================

Contract tests for SciOS Runtime ToolExecutor.
"""

from scios.runtime.tools import (
    Tool,
    ToolExecutor,
    ToolPolicy,
    ToolRegistry,
    ToolResult,
    ToolSandbox,
)


# ==========================================================
# Test Tools
# ==========================================================


class EchoTool(Tool):

    NAME = "echo"

    def execute(
        self,
        value,
    ):
        return value


class FailingTool(Tool):

    NAME = "failing"

    def execute(self):

        raise RuntimeError(
            "tool failed"
        )


# ==========================================================
# Construction
# ==========================================================


def test_executor_default_components():

    executor = ToolExecutor()

    assert isinstance(
        executor.registry,
        ToolRegistry,
    )

    assert isinstance(
        executor.policy,
        ToolPolicy,
    )

    assert isinstance(
        executor.sandbox,
        ToolSandbox,
    )

    assert executor.executions == 0
    assert executor.success == 0
    assert executor.failed == 0


def test_executor_custom_components():

    registry = ToolRegistry()
    policy = ToolPolicy()
    sandbox = ToolSandbox(
        policy=policy
    )

    executor = ToolExecutor(
        registry=registry,
        policy=policy,
        sandbox=sandbox,
    )

    assert executor.registry is registry
    assert executor.policy is policy
    assert executor.sandbox is sandbox


# ==========================================================
# Registration / Discovery
# ==========================================================


def test_executor_run():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry,
        sandbox=ToolSandbox(),
        policy=ToolPolicy(),
    )

    result = executor.execute(
        "echo",
        value="hello",
    )

    assert result.value == "hello"


def test_available_tools():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry
    )

    assert executor.available_tools() == [
        "echo"
    ]


def test_has_tool():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry
    )

    assert executor.has_tool(
        "echo"
    ) is True

    assert executor.has_tool(
        "missing"
    ) is False


# ==========================================================
# Execute By Name
# ==========================================================


def test_execute_returns_tool_result():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry
    )

    result = executor.execute(
        "echo",
        value="hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"


def test_execute_unknown_tool():

    executor = ToolExecutor()

    result = executor.execute(
        "missing"
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        KeyError,
    )

    assert "Unknown tool" in str(
        result.error
    )


def test_unknown_tool_updates_statistics():

    executor = ToolExecutor()

    result = executor.execute(
        "missing"
    )

    assert result.success is False
    assert executor.executions == 1
    assert executor.success == 0
    assert executor.failed == 1


# ==========================================================
# Execute Tool Instance
# ==========================================================


def test_execute_tool_instance():

    executor = ToolExecutor()

    tool = EchoTool()

    result = executor.execute_tool(
        tool,
        value="hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"


def test_execute_failing_tool():

    executor = ToolExecutor()

    tool = FailingTool()

    result = executor.execute_tool(
        tool
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


# ==========================================================
# Statistics
# ==========================================================


def test_success_statistics():

    executor = ToolExecutor()

    result = executor.execute_tool(
        EchoTool(),
        value="ok",
    )

    assert result.success is True
    assert executor.executions == 1
    assert executor.success == 1
    assert executor.failed == 0


def test_failure_statistics():

    executor = ToolExecutor()

    result = executor.execute_tool(
        FailingTool()
    )

    assert result.success is False
    assert executor.executions == 1
    assert executor.success == 0
    assert executor.failed == 1


def test_multiple_statistics():

    executor = ToolExecutor()

    executor.execute_tool(
        EchoTool(),
        value="one",
    )

    executor.execute_tool(
        EchoTool(),
        value="two",
    )

    executor.execute_tool(
        FailingTool()
    )

    assert executor.executions == 3
    assert executor.success == 2
    assert executor.failed == 1


# ==========================================================
# Policy Integration
# ==========================================================


def test_executor_respects_policy():

    policy = ToolPolicy()

    policy.deny_tool(
        "echo"
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry,
        policy=policy,
        sandbox=sandbox,
    )

    result = executor.execute(
        "echo",
        value="blocked",
    )

    assert result.success is False
    assert isinstance(
        result.error,
        PermissionError,
    )

    assert executor.executions == 1
    assert executor.failed == 1


def test_executor_respects_call_limit():

    policy = ToolPolicy(
        max_calls=1
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry,
        policy=policy,
        sandbox=sandbox,
    )

    first = executor.execute(
        "echo",
        value="first",
    )

    second = executor.execute(
        "echo",
        value="second",
    )

    assert first.success is True
    assert second.success is False

    assert executor.executions == 2
    assert executor.success == 1
    assert executor.failed == 1


# ==========================================================
# Batch Execution
# ==========================================================


def test_execute_many():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry
    )

    results = executor.execute_many(
        "echo",
        [
            {"value": "a"},
            {"value": "b"},
            {"value": "c"},
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
        "a",
        "b",
        "c",
    ]

    assert executor.executions == 3
    assert executor.success == 3
    assert executor.failed == 0


def test_execute_many_unknown_tool():

    executor = ToolExecutor()

    results = executor.execute_many(
        "missing",
        [
            {},
            {},
        ],
    )

    assert len(results) == 2

    assert all(
        result.success is False
        for result in results
    )

    assert executor.executions == 2
    assert executor.failed == 2


# ==========================================================
# Lifecycle
# ==========================================================


def test_initialize():

    executor = ToolExecutor()

    tool = EchoTool()

    executor.registry.register(
        tool
    )

    executor.initialize()

    assert executor.has_tool(
        "echo"
    )


def test_shutdown():

    executor = ToolExecutor()

    tool = EchoTool()

    executor.registry.register(
        tool
    )

    executor.shutdown()

    assert executor.has_tool(
        "echo"
    )


# ==========================================================
# Diagnostics
# ==========================================================


def test_status():

    executor = ToolExecutor()

    executor.execute_tool(
        EchoTool(),
        value="hello",
    )

    status = executor.status()

    assert status["executions"] == 1
    assert status["success"] == 1
    assert status["failed"] == 0
    assert status["tools"] == []


def test_status_with_tools():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    executor = ToolExecutor(
        registry=registry
    )

    status = executor.status()

    assert status["tools"] == [
        "echo"
    ]


# ==========================================================
# Protocol
# ==========================================================


def test_len():

    executor = ToolExecutor()

    assert len(executor) == 0

    executor.execute_tool(
        EchoTool(),
        value="hello",
    )

    assert len(executor) == 1


def test_bool():

    executor = ToolExecutor()

    assert bool(executor) is False

    executor.execute_tool(
        EchoTool(),
        value="hello",
    )

    assert bool(executor) is True


def test_repr():

    executor = ToolExecutor()

    representation = repr(
        executor
    )

    assert "ToolExecutor" in representation
    assert "executions=0" in representation