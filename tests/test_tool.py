# tests/test_tool.py

import time
import pytest

from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.response import ToolResponse
from scios.cognitive_core.tool_use.state import ToolState
from scios.cognitive_core.tool_use.history import ToolHistory
from scios.cognitive_core.tool_use.metrics import ToolMetrics


def test_tool_request_to_dict():
    req = ToolRequest(tool="calculator", action="evaluate", params={"expression": "2+2"})
    data = req.to_dict()
    assert data["tool"] == "calculator"
    assert data["action"] == "evaluate"
    assert data["params"]["expression"] == "2+2"


def test_tool_response_success_and_error():
    resp_success = ToolResponse.success(tool="calculator", result=4)
    assert resp_success.status == "success"
    assert resp_success.result == 4

    resp_error = ToolResponse.error(tool="filesystem", message="Permission denied")
    assert resp_error.status == "error"
    assert resp_error.message == "Permission denied"


def test_tool_state_transitions():
    state = ToolState("calculator")
    assert state.status == "idle"

    req = {"tool": "calculator", "action": "evaluate"}
    state.set_running(req)
    assert state.status == "running"
    assert state.last_request == req

    resp = {"status": "success", "result": 4}
    state.set_success(resp)
    assert state.status == "success"
    assert state.last_response == resp

    state.reset()
    assert state.status == "idle"
    assert state.last_request is None


def test_tool_history_log_and_filter():
    history = ToolHistory()
    req = {"tool": "calculator", "action": "evaluate"}
    resp = {"status": "success", "result": 4}
    history.log("calculator", req, resp)

    entries = history.list()
    assert len(entries) == 1
    assert entries[0]["tool"] == "calculator"

    filtered = history.filter_by_tool("calculator")
    assert len(filtered) == 1

    history.clear()
    assert history.list() == []


def test_tool_metrics_record_and_get():
    metrics = ToolMetrics()
    start = time.time()
    metrics.record("calculator", start, success=True)

    stats = metrics.get_metrics("calculator")
    assert stats["calls"] == 1
    assert stats["success"] == 1
    assert stats["failure"] == 0
    assert stats["avg_time"] >= 0.0
