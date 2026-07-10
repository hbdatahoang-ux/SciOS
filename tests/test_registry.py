# tests/test_registry.py

import pytest
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.base import Tool


class DummyTool(Tool):
    name = "dummy"
    description = "A dummy test tool"

    def validate(self, request):
        return True

    def execute(self, request):
        return {"status": "success", "result": "ok"}


def test_register_and_list_tools():
    registry = ToolRegistry()
    tool = DummyTool()

    registry.register(tool)
    tools = registry.list_tools()

    assert "dummy" in tools
    assert tools["dummy"] == "A dummy test tool"


def test_get_tool():
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)

    retrieved = registry.get("dummy")
    assert isinstance(retrieved, DummyTool)
    assert retrieved.name == "dummy"


def test_unregister_tool():
    registry = ToolRegistry()
    tool = DummyTool()
    registry.register(tool)

    registry.unregister("dummy")
    assert "dummy" not in registry.list_tools()


def test_get_nonexistent_tool_returns_none():
    registry = ToolRegistry()
    assert registry.get("nonexistent") is None
