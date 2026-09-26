import pytest

from scios.cognitive_core.tool_use.response import ToolResponse


def test_response_creation():
    response = ToolResponse(
        tool="calculator",
        status="success",
        result=5,
        message=None,
        metadata={"source": "test"},
    )

    assert response.tool == "calculator"
    assert response.status == "success"
    assert response.result == 5
    assert response.message is None
    assert response.metadata == {"source": "test"}


def test_response_defaults():
    response = ToolResponse(
        tool="calculator",
        status="success",
    )

    assert response.result is None
    assert response.message is None
    assert response.metadata == {}


def test_response_strips_tool():
    response = ToolResponse(
        tool="  calculator  ",
        status="success",
    )

    assert response.tool == "calculator"


@pytest.mark.parametrize(
    "tool",
    ["", "   ", None, 123],
)
def test_response_rejects_invalid_tool(tool):
    with pytest.raises(ValueError, match="Tool name cannot be empty"):
        ToolResponse(
            tool=tool,
            status="success",
        )


def test_response_rejects_non_string_status():
    with pytest.raises(ValueError, match="Status must be string"):
        ToolResponse(
            tool="calculator",
            status=123,
        )


@pytest.mark.parametrize(
    "status",
    ["", "unknown", "pending", "failed"],
)
def test_response_rejects_invalid_status(status):
    with pytest.raises(ValueError, match="Invalid status"):
        ToolResponse(
            tool="calculator",
            status=status,
        )


@pytest.mark.parametrize(
    "status",
    ["SUCCESS", " Success ", "success"],
)
def test_response_normalizes_status(status):
    response = ToolResponse(
        tool="calculator",
        status=status,
    )

    assert response.status == "success"


def test_success_factory():
    response = ToolResponse.success(
        tool="calculator",
        result=5,
        metadata={"source": "test"},
    )

    assert response.tool == "calculator"
    assert response.status == "success"
    assert response.result == 5
    assert response.message is None
    assert response.metadata == {"source": "test"}
    assert response.is_success()
    assert not response.is_error()


def test_error_factory():
    response = ToolResponse.error(
        tool="calculator",
        message="Calculation failed",
        metadata={"source": "test"},
    )

    assert response.tool == "calculator"
    assert response.status == "error"
    assert response.result is None
    assert response.message == "Calculation failed"
    assert response.metadata == {"source": "test"}
    assert response.is_error()
    assert not response.is_success()


def test_success_and_error_states_are_mutually_exclusive():
    success = ToolResponse.success(
        tool="calculator",
        result=5,
    )

    error = ToolResponse.error(
        tool="calculator",
        message="failed",
    )

    assert success.is_success()
    assert not success.is_error()

    assert error.is_error()
    assert not error.is_success()


def test_to_dict():
    response = ToolResponse(
        tool="calculator",
        status="success",
        result=5,
        message=None,
        metadata={"source": "test"},
    )

    assert response.to_dict() == {
        "tool": "calculator",
        "status": "success",
        "result": 5,
        "message": None,
        "metadata": {"source": "test"},
    }


def test_to_dict_returns_metadata_copy():
    response = ToolResponse.success(
        tool="calculator",
        result=5,
        metadata={"source": "test"},
    )

    data = response.to_dict()

    data["metadata"]["source"] = "changed"

    assert response.metadata == {"source": "test"}


def test_constructor_copies_metadata():
    metadata = {"source": "test"}

    response = ToolResponse.success(
        tool="calculator",
        result=5,
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert response.metadata == {"source": "test"}


def test_from_dict():
    data = {
        "tool": "calculator",
        "status": "success",
        "result": 5,
        "message": None,
        "metadata": {"source": "test"},
    }

    response = ToolResponse.from_dict(data)

    assert response == ToolResponse.success(
        tool="calculator",
        result=5,
        metadata={"source": "test"},
    )


def test_round_trip():
    original = ToolResponse.error(
        tool="calculator",
        message="Calculation failed",
        metadata={"source": "test"},
    )

    restored = ToolResponse.from_dict(
        original.to_dict()
    )

    assert restored == original


def test_response_equality():
    first = ToolResponse.success(
        tool="calculator",
        result=5,
        metadata={"source": "test"},
    )

    second = ToolResponse.success(
        tool="calculator",
        result=5,
        metadata={"source": "test"},
    )

    assert first == second


def test_response_inequality():
    first = ToolResponse.success(
        tool="calculator",
        result=5,
    )

    second = ToolResponse.success(
        tool="calculator",
        result=6,
    )

    assert first != second


def test_response_equality_with_other_type():
    response = ToolResponse.success(
        tool="calculator",
        result=5,
    )

    assert response != {}


def test_response_repr():
    response = ToolResponse.success(
        tool="calculator",
        result=5,
    )

    assert repr(response) == (
        "<ToolResponse "
        "tool='calculator' "
        "status='success'>"
    )
