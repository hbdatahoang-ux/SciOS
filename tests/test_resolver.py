# tests/test_resolver.py

import pytest
from scios.cognitive_core.tool_use.resolver import ToolResolver
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.base import Tool


class DummyTool(Tool):
    name = "dummy"
    description = "A dummy test tool"

    def validate(self, request):
        return "action" in request

    def execute(self, request):
        return {"status": "success", "result": "dummy executed"}


def setup_registry_with_dummy():
    registry = ToolRegistry()
    registry.register(DummyTool())
    return registry


def test_resolver_resolves_existing_tool():
    registry = setup_registry_with_dummy()
    resolver = ToolResolver(registry)

    request = {"tool": "dummy", "action": "run"}
    tool = resolver.resolve(request)

    assert isinstance(tool, DummyTool)
    assert tool.name == "dummy"


def test_resolver_returns_none_for_unknown_tool():
    registry = setup_registry_with_dummy()
    resolver = ToolResolver(registry)

    request = {"tool": "nonexistent", "action": "run"}
    tool = resolver.resolve(request)

    assert tool is None


def test_resolver_executes_tool_successfully():
    registry = setup_registry_with_dummy()
    resolver = ToolResolver(registry)

    request = {"tool": "dummy", "action": "run"}
    tool = resolver.resolve(request)
    response = tool.execute(request)

    assert response["status"] == "success"
    assert response["result"] == "dummy executed"


def test_resolver_tool_validation():
    registry = setup_registry_with_dummy()
    resolver = ToolResolver(registry)

    # Request thiếu action → validate sẽ fail
    request = {"tool": "dummy"}
    tool = resolver.resolve(request)

    assert tool is not None
    assert tool.validate(request) is False
