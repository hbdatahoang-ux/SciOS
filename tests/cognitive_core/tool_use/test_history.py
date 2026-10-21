# tests/cognitive_core/tool_use/test_history.py

import pytest

from scios.cognitive_core.tool_use.history import (
    ToolHistory,
    ToolHistoryEntry,
)
from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.response import ToolResponse


def make_request(
    tool="calculator",
    action="calculate",
    params=None,
    metadata=None,
):
    return ToolRequest(
        tool=tool,
        action=action,
        params=params or {},
        metadata=metadata or {},
    )


def make_response(
    tool="calculator",
    result=5,
):
    return ToolResponse.success(
        tool=tool,
        result=result,
    )


def test_history_entry_stores_request_and_response():
    request = make_request()
    response = make_response()

    entry = ToolHistoryEntry(request, response)

    assert entry.request is request
    assert entry.response is response
    assert entry.tool == "calculator"
    assert isinstance(entry.timestamp, float)


def test_history_entry_rejects_invalid_request():
    response = make_response()

    with pytest.raises(TypeError, match="request must be a ToolRequest"):
        ToolHistoryEntry({}, response)


def test_history_entry_rejects_invalid_response():
    request = make_request()

    with pytest.raises(TypeError, match="response must be a ToolResponse"):
        ToolHistoryEntry(request, {})


def test_history_entry_to_dict():
    request = make_request(
        params={"a": 2, "b": 3},
        metadata={"source": "test"},
    )
    response = make_response(result=5)

    entry = ToolHistoryEntry(
        request,
        response,
        timestamp=123.456,
    )

    assert entry.to_dict() == {
        "tool": "calculator",
        "request": {
            "tool": "calculator",
            "action": "calculate",
            "params": {"a": 2, "b": 3},
            "metadata": {"source": "test"},
        },
        "response": {
            "tool": "calculator",
            "status": "success",
            "result": 5,
            "message": None,
            "metadata": {},
        },
        "timestamp": 123.456,
    }


def test_history_log_creates_entry():
    history = ToolHistory()
    request = make_request()
    response = make_response()

    entry = history.log(request, response, timestamp=100.0)

    assert isinstance(entry, ToolHistoryEntry)
    assert len(history) == 1
    assert history.entries[0] is entry
    assert entry.request is request
    assert entry.response is response
    assert entry.timestamp == 100.0


def test_history_log_rejects_invalid_request():
    history = ToolHistory()
    response = make_response()

    with pytest.raises(TypeError, match="request must be a ToolRequest"):
        history.log({}, response)


def test_history_log_rejects_invalid_response():
    history = ToolHistory()
    request = make_request()

    with pytest.raises(TypeError, match="response must be a ToolResponse"):
        history.log(request, {})


def test_history_list_returns_serialized_entries():
    history = ToolHistory()

    request = make_request(
        params={"expression": "2+2"},
    )
    response = make_response(result=4)

    history.log(
        request,
        response,
        timestamp=200.0,
    )

    result = history.list()

    assert len(result) == 1
    assert result[0]["tool"] == "calculator"
    assert result[0]["request"]["action"] == "calculate"
    assert result[0]["request"]["params"] == {
        "expression": "2+2",
    }
    assert result[0]["response"]["status"] == "success"
    assert result[0]["response"]["result"] == 4
    assert result[0]["timestamp"] == 200.0


def test_history_filter_by_tool():
    history = ToolHistory()

    history.log(
        make_request(tool="calculator"),
        make_response(tool="calculator", result=5),
        timestamp=1.0,
    )

    history.log(
        make_request(tool="echo", action="say"),
        make_response(tool="echo", result="hello"),
        timestamp=2.0,
    )

    history.log(
        make_request(tool="calculator", action="evaluate"),
        make_response(tool="calculator", result=9),
        timestamp=3.0,
    )

    calculator_entries = history.filter_by_tool("calculator")

    assert len(calculator_entries) == 2
    assert all(
        entry["tool"] == "calculator"
        for entry in calculator_entries
    )


def test_history_filter_by_unknown_tool_returns_empty():
    history = ToolHistory()

    history.log(
        make_request(),
        make_response(),
    )

    assert history.filter_by_tool("unknown") == []


def test_history_clear():
    history = ToolHistory()

    history.log(
        make_request(),
        make_response(),
    )

    assert len(history) == 1

    history.clear()

    assert len(history) == 0
    assert history.entries == []


def test_history_repr():
    history = ToolHistory()

    assert repr(history) == "<ToolHistory entries=0>"

    history.log(
        make_request(),
        make_response(),
    )

    assert repr(history) == "<ToolHistory entries=1>"


def test_history_entry_repr():
    entry = ToolHistoryEntry(
        make_request(),
        make_response(),
        timestamp=123.456,
    )

    text = repr(entry)

    assert "calculator" in text
    assert "success" in text
    assert "123.456" in text


def test_history_preserves_multiple_tools():
    history = ToolHistory()

    history.log(
        make_request(tool="calculator"),
        make_response(tool="calculator", result=5),
    )

    history.log(
        make_request(tool="filesystem", action="read"),
        ToolResponse.success(
            tool="filesystem",
            result="content",
        ),
    )

    assert len(history) == 2
    assert history.entries[0].tool == "calculator"
    assert history.entries[1].tool == "filesystem"
