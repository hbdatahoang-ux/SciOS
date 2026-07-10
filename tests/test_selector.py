# tests/test_selector.py

import pytest
from scios.cognitive_core.tool_use.selector import ToolSelector
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.base import Tool


class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate math expressions"

    def validate(self, request):
        return "expression" in request.get("params", {})

    def execute(self, request):
        expr = request["params"]["expression"]
        return {"status": "success", "result": eval(expr)}


class EchoTool(Tool):
    name = "echo"
    description = "Echo back input"

    def validate(self, request):
        return "message" in request.get("params", {})

    def execute(self, request):
        return {"status": "success", "result": request["params"]["message"]}


def setup_registry():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(EchoTool())
    return registry


def test_selector_selects_calculator_tool():
    registry = setup_registry()
    selector = ToolSelector(registry)

    request = {"tool": "calculator", "action": "evaluate", "params": {"expression": "2+2"}}
    tool = selector.select(request)

    assert isinstance(tool, CalculatorTool)
    assert tool.name == "calculator"


def test_selector_selects_echo_tool():
    registry = setup_registry()
    selector = ToolSelector(registry)

    request = {"tool": "echo", "action": "say", "params": {"message": "hello"}}
    tool = selector.select(request)

    assert isinstance(tool, EchoTool)
    assert tool.name == "echo"


def test_selector_returns_none_for_invalid_request():
    registry = setup_registry()
    selector = ToolSelector(registry)

    # Request không hợp lệ (thiếu params)
    request = {"tool": "calculator", "action": "evaluate"}
    tool = selector.select(request)

    assert tool is None


def test_selector_returns_none_for_unknown_tool():
    registry = setup_registry()
    selector = ToolSelector(registry)

    request = {"tool": "nonexistent", "action": "run"}
    tool = selector.select(request)

    assert tool is None
