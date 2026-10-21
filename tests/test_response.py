# tests/test_response.py

import pytest
from scios.cognitive_core.tool_use.response import ToolResponse


def test_response_success_initialization_and_schema():
    resp = ToolResponse.success(tool="calculator", result=4)
    assert resp.status == "success"
    assert resp.tool == "calculator"
    assert resp.result == 4
    assert resp.message is None

    data = resp.to_dict()
    required_keys = {"status", "tool", "result", "message"}
    assert required_keys.issubset(data.keys())
    assert data["status"] == "success"
    assert data["result"] == 4


def test_response_error_initialization_and_schema():
    resp = ToolResponse.error(tool="filesystem", message="Permission denied")
    assert resp.status == "error"
    assert resp.tool == "filesystem"
    assert resp.result is None
    assert resp.message == "Permission denied"

    data = resp.to_dict()
    assert data["status"] == "error"
    assert data["message"] == "Permission denied"


def test_response_repr_contains_status_and_tool():
    resp = ToolResponse.success(tool="echo", result="hello")
    repr_str = repr(resp)
    assert "success" in repr_str
    assert "echo" in repr_str


def test_response_multiple_responses_consistency():
    r1 = ToolResponse.success(tool="network", result="pong")
    r2 = ToolResponse.error(tool="database", message="Connection failed")

    d1 = r1.to_dict()
    d2 = r2.to_dict()

    assert d1["status"] == "success"
    assert d1["result"] == "pong"
    assert d2["status"] == "error"
    assert "Connection failed" in d2["message"]


def test_response_invalid_status_raises():
    # Nếu ToolResponse không cho phép status ngoài "success"/"error"
    with pytest.raises(ValueError):
        ToolResponse(tool="dummy", status="invalid", result=None, message=None)
