import pytest

from scios.cognitive_core.tool_use.request import ToolRequest


def test_request_creation():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2, "b": 3},
        metadata={"source": "test"},
    )

    assert request.tool == "calculator"
    assert request.action == "calculate"
    assert request.params == {"a": 2, "b": 3}
    assert request.metadata == {"source": "test"}


def test_request_defaults():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
    )

    assert request.params == {}
    assert request.metadata == {}


@pytest.mark.parametrize(
    "tool",
    ["", "   ", None, 123],
)
def test_request_rejects_invalid_tool(tool):
    with pytest.raises(ValueError, match="Tool name cannot be empty"):
        ToolRequest(
            tool=tool,
            action="calculate",
        )


@pytest.mark.parametrize(
    "action",
    ["", "   ", None, 123],
)
def test_request_rejects_invalid_action(action):
    with pytest.raises(ValueError, match="Tool action cannot be empty"):
        ToolRequest(
            tool="calculator",
            action=action,
        )


def test_request_strips_tool_and_action():
    request = ToolRequest(
        tool="  calculator  ",
        action="  calculate  ",
    )

    assert request.tool == "calculator"
    assert request.action == "calculate"


def test_request_copies_params_and_metadata():
    params = {"value": 10}
    metadata = {"source": "test"}

    request = ToolRequest(
        tool="calculator",
        action="calculate",
        params=params,
        metadata=metadata,
    )

    params["value"] = 99
    metadata["source"] = "changed"

    assert request.params == {"value": 10}
    assert request.metadata == {"source": "test"}


def test_parameters_is_compatibility_alias():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 1},
    )

    assert request.parameters == {"a": 1}

    request.parameters = {"a": 2}

    assert request.params == {"a": 2}
    assert request.parameters == {"a": 2}


def test_to_dict():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2, "b": 3},
        metadata={"source": "test"},
    )

    assert request.to_dict() == {
        "tool": "calculator",
        "action": "calculate",
        "params": {"a": 2, "b": 3},
        "metadata": {"source": "test"},
    }


def test_to_dict_returns_copies():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2},
        metadata={"source": "test"},
    )

    data = request.to_dict()

    data["params"]["a"] = 99
    data["metadata"]["source"] = "changed"

    assert request.params == {"a": 2}
    assert request.metadata == {"source": "test"}


def test_from_dict():
    data = {
        "tool": "calculator",
        "action": "calculate",
        "params": {"a": 2, "b": 3},
        "metadata": {"source": "test"},
    }

    request = ToolRequest.from_dict(data)

    assert request == ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2, "b": 3},
        metadata={"source": "test"},
    )


def test_from_dict_supports_parameters_compatibility_alias():
    request = ToolRequest.from_dict(
        {
            "tool": "calculator",
            "action": "calculate",
            "parameters": {"a": 2},
        }
    )

    assert request.params == {"a": 2}


def test_from_dict_prefers_params_over_parameters():
    request = ToolRequest.from_dict(
        {
            "tool": "calculator",
            "action": "calculate",
            "params": {"a": 2},
            "parameters": {"a": 99},
        }
    )

    assert request.params == {"a": 2}


def test_from_context():
    request = ToolRequest.from_context(
        {
            "tool": "calculator",
            "action": "calculate",
            "params": {"a": 2},
            "metadata": {"source": "pipeline"},
        }
    )

    assert request == ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2},
        metadata={"source": "pipeline"},
    )


def test_from_context_supports_legacy_operation_input():
    request = ToolRequest.from_context(
        {
            "tool": "calculator",
            "operation": "calculate",
            "params": {"a": 2},
        }
    )

    assert request.action == "calculate"


def test_from_context_prefers_action_over_operation():
    request = ToolRequest.from_context(
        {
            "tool": "calculator",
            "action": "calculate",
            "operation": "legacy_operation",
        }
    )

    assert request.action == "calculate"


def test_update_metadata():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
    )

    request.update_metadata(
        source="test",
        priority=1,
    )

    assert request.metadata == {
        "source": "test",
        "priority": 1,
    }


def test_request_round_trip():
    original = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2, "b": 3},
        metadata={"source": "test"},
    )

    restored = ToolRequest.from_dict(original.to_dict())

    assert restored == original


def test_request_equality():
    first = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2},
        metadata={"source": "test"},
    )

    second = ToolRequest(
        tool="calculator",
        action="calculate",
        params={"a": 2},
        metadata={"source": "test"},
    )

    assert first == second


def test_request_inequality():
    first = ToolRequest(
        tool="calculator",
        action="calculate",
    )

    second = ToolRequest(
        tool="calculator",
        action="other",
    )

    assert first != second


def test_request_repr():
    request = ToolRequest(
        tool="calculator",
        action="calculate",
    )

    assert repr(request) == (
        "<ToolRequest tool='calculator' action='calculate'>"
    )


@pytest.mark.parametrize(
    "value",
    [[], "invalid"],
)
def test_request_rejects_invalid_params(value):
    with pytest.raises(TypeError, match="Tool params"):
        ToolRequest(
            tool="calculator",
            action="calculate",
            params=value,
        )


@pytest.mark.parametrize(
    "value",
    [[], "invalid"],
)
def test_request_rejects_invalid_metadata(value):
    with pytest.raises(TypeError, match="Tool metadata"):
        ToolRequest(
            tool="calculator",
            action="calculate",
            metadata=value,
        )


def test_from_dict_rejects_non_dict():
    with pytest.raises(TypeError, match="Tool request data"):
        ToolRequest.from_dict(None)


def test_from_context_rejects_non_dict():
    with pytest.raises(TypeError, match="Tool context"):
        ToolRequest.from_context(None)
