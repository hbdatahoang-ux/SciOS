"""
ToolRegistry tests
==================

Contract tests for SciOS Runtime ToolRegistry.

Covered contracts:
- construction
- registration
- type validation
- duplicate protection
- lookup
- required lookup
- existence
- unregister
- enable / disable
- collection API
- clear
- lifecycle
- diagnostics
- protocol methods
"""


import pytest


from scios.runtime.tools import (
    Tool,
    ToolRegistry,
)


# ==========================================================
# Test Tools
# ==========================================================


class EchoTool(Tool):

    NAME = "echo"
    DESCRIPTION = "Echo tool"
    VERSION = "1.0.0"

    def execute(
        self,
        value,
    ):
        return value


class SecondTool(Tool):

    NAME = "second"

    def execute(self):
        return "second"


class LifecycleTool(Tool):

    NAME = "lifecycle"

    def __init__(self):
        super().__init__()

        self.initialized = 0
        self.shutdown_count = 0

    def initialize(self):
        self.initialized += 1

    def shutdown(self):
        self.shutdown_count += 1

    def execute(self):
        return "ok"


# ==========================================================
# Construction
# ==========================================================


def test_registry_initially_empty():

    registry = ToolRegistry()

    assert registry.count == 0
    assert len(registry) == 0
    assert registry.list() == []
    assert registry.values() == []


# ==========================================================
# Register
# ==========================================================


def test_register_tool():

    registry = ToolRegistry()

    tool = EchoTool()

    returned = registry.register(
        tool
    )

    assert returned is tool
    assert registry.exists(
        "echo"
    )

    assert registry.get(
        "echo"
    ) is tool

    assert registry.count == 1


def test_register_rejects_non_tool():

    registry = ToolRegistry()

    with pytest.raises(
        TypeError,
        match="Only Tool instances can be registered",
    ):
        registry.register(
            "not-a-tool"
        )


def test_register_duplicate_tool():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    with pytest.raises(
        ValueError,
        match="Tool already registered: echo",
    ):
        registry.register(
            EchoTool()
        )


def test_register_initializes_tool():

    registry = ToolRegistry()

    tool = LifecycleTool()

    registry.register(
        tool
    )

    assert tool.initialized == 1


# ==========================================================
# Lookup
# ==========================================================


def test_get_tool():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    loaded = registry.get(
        "echo"
    )

    assert loaded is tool


def test_get_unknown_tool_returns_none():

    registry = ToolRegistry()

    assert registry.get(
        "unknown"
    ) is None


def test_get_unknown_tool_default():

    registry = ToolRegistry()

    default = object()

    assert registry.get(
        "unknown",
        default,
    ) is default


def test_require_existing_tool():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    assert registry.require(
        "echo"
    ) is tool


def test_require_unknown_tool():

    registry = ToolRegistry()

    with pytest.raises(
        KeyError,
        match="Unknown tool: unknown",
    ):
        registry.require(
            "unknown"
        )


# ==========================================================
# Existence
# ==========================================================


def test_exists():

    registry = ToolRegistry()

    assert registry.exists(
        "echo"
    ) is False

    registry.register(
        EchoTool()
    )

    assert registry.exists(
        "echo"
    ) is True


# ==========================================================
# Unregister
# ==========================================================


def test_unregister():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    removed = registry.unregister(
        "echo"
    )

    assert removed is tool
    assert not registry.exists(
        "echo"
    )
    assert registry.count == 0


def test_unregister_unknown_tool():

    registry = ToolRegistry()

    assert registry.unregister(
        "unknown"
    ) is None


def test_unregister_shutdowns_tool():

    registry = ToolRegistry()

    tool = LifecycleTool()

    registry.register(
        tool
    )

    registry.unregister(
        "lifecycle"
    )

    assert tool.shutdown_count == 1


# ==========================================================
# Enable / Disable
# ==========================================================


def test_disable_tool():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    registry.disable(
        "echo"
    )

    assert tool.enabled is False


def test_enable_tool():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    registry.disable(
        "echo"
    )

    registry.enable(
        "echo"
    )

    assert tool.enabled is True


def test_enable_unknown_tool():

    registry = ToolRegistry()

    with pytest.raises(
        KeyError,
        match="Unknown tool: unknown",
    ):
        registry.enable(
            "unknown"
        )


def test_disable_unknown_tool():

    registry = ToolRegistry()

    with pytest.raises(
        KeyError,
        match="Unknown tool: unknown",
    ):
        registry.disable(
            "unknown"
        )


# ==========================================================
# Collection API
# ==========================================================


def test_list_tools():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    registry.register(
        SecondTool()
    )

    assert registry.list() == [
        "echo",
        "second",
    ]


def test_values_tools():

    registry = ToolRegistry()

    first = EchoTool()
    second = SecondTool()

    registry.register(first)
    registry.register(second)

    values = registry.values()

    assert values == [
        first,
        second,
    ]


def test_registry_iteration():

    registry = ToolRegistry()

    first = EchoTool()
    second = SecondTool()

    registry.register(first)
    registry.register(second)

    assert list(registry) == [
        first,
        second,
    ]


def test_registry_contains():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    assert "echo" in registry
    assert "unknown" not in registry


# ==========================================================
# Clear
# ==========================================================


def test_clear():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    registry.register(
        SecondTool()
    )

    registry.clear()

    assert registry.count == 0
    assert registry.list() == []
    assert registry.values() == []


def test_clear_shutdowns_all_tools():

    registry = ToolRegistry()

    first = LifecycleTool()

    class AnotherLifecycleTool(LifecycleTool):
        NAME = "another"

    second = AnotherLifecycleTool()

    registry.register(first)
    registry.register(second)

    registry.clear()

    assert first.shutdown_count == 1
    assert second.shutdown_count == 1


def test_clear_empty_registry():

    registry = ToolRegistry()

    registry.clear()

    assert registry.count == 0


# ==========================================================
# Diagnostics
# ==========================================================


def test_status_empty():

    registry = ToolRegistry()

    status = registry.status()

    assert status["count"] == 0
    assert status["tools"] == []


def test_status():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    status = registry.status()

    assert status["count"] == 1
    assert len(status["tools"]) == 1

    data = status["tools"][0]

    assert data["id"] == tool.id
    assert data["name"] == "echo"
    assert data["version"] == "1.0.0"


def test_health():

    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    health = registry.health()

    assert "echo" in health
    assert health["echo"]["id"] == tool.id
    assert health["echo"]["name"] == "echo"
    assert health["echo"]["enabled"] is True


# ==========================================================
# Representation
# ==========================================================


def test_registry_repr():

    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    representation = repr(
        registry
    )

    assert "ToolRegistry" in representation
    assert "echo" in representation