# tests/test_request.py

import pytest
from scios.cognitive_core.tool_use.request import ToolRequest


def test_request_initialization_and_schema():
    req = ToolRequest(tool="calculator", action="evaluate", params={"expression": "2+2"})
    assert req.tool == "calculator"
    assert req.action == "evaluate"
    assert req.params == {"expression": "2+2"}

    data = req.to_dict()
    required_keys = {"tool", "action", "params"}
    assert required_keys.issubset(data.keys())


def test_request_with_empty_params():
    req = ToolRequest(tool="echo", action="say", params={})
    data = req.to_dict()
    assert data["tool"] == "echo"
    assert data["action"] == "say"
    assert data["params"] == {}


def test_request_repr_contains_tool_and_action():
    req = ToolRequest(tool="filesystem", action="read", params={"path": "/tmp/file.txt"})
    repr_str = repr(req)
    assert "filesystem" in repr_str
    assert "read" in repr_str


def test_request_multiple_requests_consistency():
    req1 = ToolRequest(tool="network", action="ping", params={"host": "localhost"})
    req2 = ToolRequest(tool="database", action="query", params={"sql": "SELECT 1"})

    d1 = req1.to_dict()
    d2 = req2.to_dict()

    assert d1["tool"] == "network"
    assert d1["action"] == "ping"
    assert d1["params"]["host"] == "localhost"

    assert d2["tool"] == "database"
    assert d2["action"] == "query"
    assert d2["params"]["sql"] == "SELECT 1"


def test_request_invalid_tool_or_action():
    # Nếu ToolRequest không cho phép tool/action rỗng, ta kiểm tra raise
    with pytest.raises(ValueError):
        ToolRequest(tool="", action="run", params={})

    with pytest.raises(ValueError):
        ToolRequest(tool="dummy", action="", params={})
