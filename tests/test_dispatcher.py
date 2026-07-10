# tests/test_dispatcher.py

import pytest
from scios.cognitive_core.tool_use.dispatcher import ToolDispatcher
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.base import Tool


class DummyTool(Tool):
    name = "dummy"
    description = "A dummy test tool"

    def validate(self, request):
        return "action" in request

    def execute(self, request):
        return {"status": "success", "result": f"executed {request['action']}"}


def setup_dispatcher():
    registry = ToolRegistry()
    registry.register(DummyTool())
    dispatcher = ToolDispatcher(registry)
    return dispatcher


def test_dispatcher_executes_tool_successfully():
    dispatcher = setup_dispatcher()
    request = {"tool": "dummy", "action": "run"}
    response = dispatcher.dispatch(request)

    assert response["status"] == "success"
    assert response["result"] == "executed run"


def test_dispatcher_returns_error_for_unknown_tool():
    dispatcher = setup_dispatcher()
    request = {"tool": "nonexistent", "action": "run"}
    response = dispatcher.dispatch(request)

    assert response["status"] == "error"
    assert "not found" in response["message"].lower()


def test_dispatcher_returns_error_for_invalid_request():
    dispatcher = setup_dispatcher()
    # Request thiếu action → validate fail
    request = {"tool": "dummy"}
    response = dispatcher.dispatch(request)

    assert response["status"] == "error"
    assert "invalid" in response["message"].lower()
