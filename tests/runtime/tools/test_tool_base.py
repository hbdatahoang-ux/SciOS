"""
Tool base contract tests
========================

Contract tests for SciOS Runtime Tool.

Covered contracts:
- class metadata
- runtime identity
- lifecycle
- enable / disable
- validation
- execution normalization
- failure handling
- execution statistics
- permissions
- schema
- diagnostics
- serialization
- callable protocol
"""


import pytest


from scios.runtime.tools import (
    Tool,
    ToolResult,
)


# ==========================================================
# Test Tools
# ==========================================================


class EchoTool(Tool):

    NAME = "echo"
    DESCRIPTION = "Echo input"
    VERSION = "1.0.0"

    def execute(
        self,
        value,
    ):
        return value


class FailingTool(Tool):

    NAME = "failing"

    def execute(self):
        raise RuntimeError(
            "execution failed"
        )


class InvalidTool(Tool):

    NAME = "invalid"

    def validate(
        self,
        **kwargs,
    ):
        return False

    def execute(self, **kwargs):
        return "should not execute"


class ResultTool(Tool):

    NAME = "result"

    def execute(self):
        return ToolResult.ok(
            "wrapped"
        )


class PermissionTool(Tool):

    NAME = "permission"

    def execute(self):
        return "ok"

    def required_permissions(self):
        return {
            "read",
            "write",
        }


# ==========================================================
# Metadata
# ==========================================================


def test_tool_metadata():

    tool = EchoTool()

    assert tool.name == "echo"
    assert tool.description == "Echo input"
    assert tool.version == "1.0.0"


# ==========================================================
# Runtime Identity
# ==========================================================


def test_tool_identity():

    tool = EchoTool()

    assert isinstance(
        tool.id,
        str,
    )

    assert tool.id

    assert isinstance(
        tool.created_at,
        str,
    )


def test_tool_instances_have_unique_ids():

    first = EchoTool()
    second = EchoTool()

    assert first.id != second.id


# ==========================================================
# Initial State
# ==========================================================


def test_tool_initial_state():

    tool = EchoTool()

    assert tool.enabled is True
    assert tool.executions == 0
    assert tool.failures == 0
    assert tool.metadata == {}


# ==========================================================
# Lifecycle
# ==========================================================


def test_tool_initialize():

    tool = EchoTool()

    assert tool.initialize() is None


def test_tool_shutdown():

    tool = EchoTool()

    assert tool.shutdown() is None


# ==========================================================
# Enable / Disable
# ==========================================================


def test_tool_disable():

    tool = EchoTool()

    tool.disable()

    assert tool.enabled is False


def test_tool_enable():

    tool = EchoTool()

    tool.disable()
    tool.enable()

    assert tool.enabled is True


def test_disabled_tool_cannot_execute():

    tool = EchoTool()

    tool.disable()

    result = tool.run(
        value="hello"
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

    assert str(result.error) == "Tool disabled"

    assert tool.executions == 0
    assert tool.failures == 0


# ==========================================================
# Validation
# ==========================================================


def test_default_validation():

    tool = EchoTool()

    assert tool.validate(
        value="hello"
    ) is True


def test_invalid_input():

    tool = InvalidTool()

    result = tool.run(
        value="hello"
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

    assert str(result.error) == "Invalid tool input"

    assert tool.executions == 0
    assert tool.failures == 0


# ==========================================================
# Execution
# ==========================================================


def test_run_normalizes_raw_value():

    tool = EchoTool()

    result = tool.run(
        value="hello"
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"

    assert tool.executions == 1
    assert tool.failures == 0


def test_run_preserves_tool_result():

    tool = ResultTool()

    result = tool.run()

    assert result.success is True
    assert result.value == "wrapped"

    assert tool.executions == 1
    assert tool.failures == 0


# ==========================================================
# Failure Handling
# ==========================================================


def test_run_catches_exception():

    tool = FailingTool()

    result = tool.run()

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is False
    assert isinstance(
        result.error,
        RuntimeError,
    )

    assert str(result.error) == "execution failed"

    assert tool.executions == 0
    assert tool.failures == 1


# ==========================================================
# Permissions
# ==========================================================


def test_default_required_permissions():

    tool = EchoTool()

    assert tool.required_permissions() == set()


def test_custom_required_permissions():

    tool = PermissionTool()

    assert tool.required_permissions() == {
        "read",
        "write",
    }


# ==========================================================
# Schema
# ==========================================================


def test_default_schema():

    tool = EchoTool()

    assert tool.schema() == {}


# ==========================================================
# Callable Protocol
# ==========================================================


def test_tool_is_callable():

    tool = EchoTool()

    result = tool(
        value="hello"
    )

    assert isinstance(
        result,
        ToolResult,
    )

    assert result.success is True
    assert result.value == "hello"

    assert tool.executions == 1


# ==========================================================
# Diagnostics
# ==========================================================


def test_tool_health():

    tool = EchoTool()

    tool.run(
        value="hello"
    )

    health = tool.health()

    assert health["id"] == tool.id
    assert health["name"] == "echo"
    assert health["version"] == "1.0.0"
    assert health["enabled"] is True
    assert health["executions"] == 1
    assert health["failures"] == 0


def test_tool_stats():

    tool = EchoTool()

    tool.run(
        value="hello"
    )

    stats = tool.stats()

    assert stats["executions"] == 1
    assert stats["failures"] == 0
    assert stats["success_rate"] == pytest.approx(
        1.0
    )


# ==========================================================
# Serialization
# ==========================================================


def test_tool_to_dict():

    tool = EchoTool()

    data = tool.to_dict()

    assert data["id"] == tool.id
    assert data["name"] == "echo"
    assert data["description"] == "Echo input"
    assert data["version"] == "1.0.0"
    assert data["enabled"] is True
    assert data["metadata"] == {}
    assert data["executions"] == 0
    assert data["failures"] == 0
    assert data["created_at"] == tool.created_at


# ==========================================================
# Representation
# ==========================================================


def test_tool_repr():

    tool = EchoTool()

    representation = repr(
        tool
    )

    assert "Tool(" in representation
    assert "echo" in representation
    assert "1.0.0" in representation
    assert "enabled=True" in representation