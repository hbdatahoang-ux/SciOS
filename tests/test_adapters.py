# tests/test_adapters.py

import pytest
from scios.cognitive_core.tool_use.adapters import RequestAdapter, ResponseAdapter
from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.response import ToolResponse


def test_request_adapter_to_dict_and_back():
    req = ToolRequest(tool="calculator", action="evaluate", params={"expression": "2+2"})
    adapter = RequestAdapter()

    data = adapter.to_dict(req)
    assert data["tool"] == "calculator"
    assert data["action"] == "evaluate"
    assert data["params"]["expression"] == "2+2"

    new_req = adapter.from_dict(data)
    assert isinstance(new_req, ToolRequest)
    assert new_req.tool == "calculator"
    assert new_req.action == "evaluate"
    assert new_req.params["expression"] == "2+2"


def test_response_adapter_to_dict_and_back_success():
    resp = ToolResponse.success(tool="echo", result="hello")
    adapter = ResponseAdapter()

    data = adapter.to_dict(resp)
    assert data["status"] == "success"
    assert data["tool"] == "echo"
    assert data["result"] == "hello"

    new_resp = adapter.from_dict(data)
    assert isinstance(new_resp, ToolResponse)
    assert new_resp.status == "success"
    assert new_resp.result == "hello"


def test_response_adapter_to_dict_and_back_error():
    resp = ToolResponse.error(tool="filesystem", message="Permission denied")
    adapter = ResponseAdapter()

    data = adapter.to_dict(resp)
    assert data["status"] == "error"
    assert data["tool"] == "filesystem"
    assert "Permission denied" in data["message"]

    new_resp = adapter.from_dict(data)
    assert new_resp.status == "error"
    assert new_resp.message == "Permission denied"


def test_request_adapter_invalid_dict_raises():
    adapter = RequestAdapter()
    invalid_data = {"tool": "dummy"}  # thiếu action và params
    with pytest.raises(ValueError):
        adapter.from_dict(invalid_data)


def test_response_adapter_invalid_dict_raises():
    adapter = ResponseAdapter()
    invalid_data = {"tool": "dummy"}  # thiếu status
    with pytest.raises(ValueError):
        adapter.from_dict(invalid_data)


def test_repr_shows_adapter_type():
    req_adapter = RequestAdapter()
    resp_adapter = ResponseAdapter()
    assert "RequestAdapter" in repr(req_adapter)
    assert "ResponseAdapter" in repr(resp_adapter)
