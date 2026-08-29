"""
ToolSandbox tests
=================

Contract tests for SciOS Runtime ToolSandbox.
"""

import time

from scios.runtime.tools import (
    Tool,
    ToolPolicy,
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


class ResultTool(Tool):

    NAME = "result"

    def execute(self):
        return ToolResult.ok(
            "already-result"
        )


class FailingTool(Tool):

    NAME = "failing"

    def execute(self):
        raise RuntimeError(
            "tool failed"
        )


# ==========================================================
# Construction
# ==========================================================


def test_sandbox_default_policy():

    sandbox = ToolSandbox()

    assert isinstance(
        sandbox.policy,
        ToolPolicy,
    )


def test_sandbox_custom_policy():

    policy = ToolPolicy(
        timeout_seconds=5.0
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    assert sandbox.policy is policy


# ==========================================================
# Callable
# ==========================================================


def test_sandbox_execute():

    sandbox = ToolSandbox()

    result = sandbox.execute(
        lambda: "ok"
    )

    assert result == "ok"


def test_callable_with_kwargs():

    sandbox = ToolSandbox()

    result = sandbox.execute(
        lambda value: value,
        value="hello",
    )

    assert result == "hello"


def test_callable_exception():

    sandbox = ToolSandbox()

    result = sandbox.execute(
        lambda: (_ for _ in ()).throw(
            RuntimeError("boom")
        )
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

    assert str(result.error) == "boom"


# ==========================================================
# Tool Object
# ==========================================================


def test_tool_run():

    sandbox = ToolSandbox()

    tool = EchoTool()

    result = sandbox.execute(
        tool,
        value="hello",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"


def test_tool_result_is_preserved():

    sandbox = ToolSandbox()

    tool = ResultTool()

    result = sandbox.execute(
        tool
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "already-result"


def test_tool_exception_is_isolated():

    sandbox = ToolSandbox()

    tool = FailingTool()

    result = sandbox.execute(
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

    assert str(result.error) == "tool failed"


# ==========================================================
# Policy
# ==========================================================


def test_policy_blocks_tool():

    policy = ToolPolicy()

    policy.deny_tool(
        "echo"
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    result = sandbox.execute(
        EchoTool(),
        value="blocked",
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        PermissionError,
    )

    assert "echo" in str(
        result.error
    )


def test_policy_records_call():

    policy = ToolPolicy()

    sandbox = ToolSandbox(
        policy=policy
    )

    assert policy.calls == 0

    sandbox.execute(
        lambda: "ok"
    )

    assert policy.calls == 1


def test_blocked_call_is_not_recorded():

    policy = ToolPolicy()

    policy.deny_tool(
        "function"
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    sandbox.execute(
        lambda: "blocked"
    )

    assert policy.calls == 0


def test_max_calls_is_enforced():

    policy = ToolPolicy(
        max_calls=1
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    first = sandbox.execute(
        lambda: "first"
    )

    second = sandbox.execute(
        lambda: "second"
    )

    assert first == "first"

    assert isinstance(
        second,
        ToolResult,
    )

    assert second.success is False
    assert isinstance(
        second.error,
        PermissionError,
    )

    assert policy.calls == 1


# ==========================================================
# Timeout
# ==========================================================


def test_timeout():

    policy = ToolPolicy(
        timeout_seconds=0.01
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    def slow():

        time.sleep(
            0.1
        )

        return "late"

    result = sandbox.execute(
        slow
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        TimeoutError,
    )

    assert "Tool timeout" in str(
        result.error
    )


# ==========================================================
# Batch Execution
# ==========================================================


def test_execute_many():

    sandbox = ToolSandbox()

    results = sandbox.execute_many(
        lambda value: value,
        [
            {"value": 1},
            {"value": 2},
            {"value": 3},
        ],
    )

    assert results == [
        1,
        2,
        3,
    ]


def test_execute_many_with_tool():

    sandbox = ToolSandbox()

    tool = EchoTool()

    results = sandbox.execute_many(
        tool,
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


def test_execute_many_preserves_failures():

    sandbox = ToolSandbox()

    tool = FailingTool()

    results = sandbox.execute_many(
        tool,
        [
            {},
            {},
        ],
    )

    assert len(results) == 2

    assert all(
        isinstance(
            result,
            ToolResult,
        )
        for result in results
    )

    assert all(
        result.success is False
        for result in results
    )


# ==========================================================
# Diagnostics
# ==========================================================


def test_status():

    policy = ToolPolicy(
        timeout_seconds=5.0
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    status = sandbox.status()

    assert "policy" in status
    assert status["policy"]["timeout_seconds"] == 5.0


def test_repr():

    policy = ToolPolicy(
        timeout_seconds=7.5
    )

    sandbox = ToolSandbox(
        policy=policy
    )

    representation = repr(
        sandbox
    )

    assert "ToolSandbox" in representation
    assert "7.5" in representation