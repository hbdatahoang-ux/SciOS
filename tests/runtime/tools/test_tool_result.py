"""
ToolResult tests
================

Contract tests for SciOS Runtime ToolResult.

Covered contracts:
- successful result
- failed result
- failure message
- failed property
- boolean protocol
- metadata
- serialization
"""


from scios.runtime.tools import ToolResult


# ==========================================================
# Factory: Success
# ==========================================================


def test_tool_result_success():

    result = ToolResult.ok(
        "hello"
    )

    assert result.success is True
    assert result.value == "hello"
    assert result.error is None
    assert result.failed is False


# ==========================================================
# Factory: Failure
# ==========================================================


def test_tool_result_failure():

    error = RuntimeError(
        "failed"
    )

    result = ToolResult.fail(
        error
    )

    assert result.success is False
    assert result.value is None
    assert result.error is error
    assert result.failed is True


# ==========================================================
# Message
# ==========================================================


def test_tool_result_success_message():

    result = ToolResult.ok(
        "hello"
    )

    assert result.message is None


def test_tool_result_failure_message():

    error = RuntimeError(
        "failed"
    )

    result = ToolResult.fail(
        error
    )

    assert result.message == "failed"


# ==========================================================
# Boolean Protocol
# ==========================================================


def test_tool_result_bool_success():

    result = ToolResult.ok(
        "hello"
    )

    assert bool(result) is True


def test_tool_result_bool_failure():

    result = ToolResult.fail(
        RuntimeError(
            "failed"
        )
    )

    assert bool(result) is False


# ==========================================================
# Metadata
# ==========================================================


def test_tool_result_metadata():

    result = ToolResult.ok(
        "hello",
        metadata={
            "source": "test",
            "count": 1,
        },
    )

    assert result.metadata == {
        "source": "test",
        "count": 1,
    }


def test_tool_result_metadata_is_independent():

    metadata = {
        "source": "test",
    }

    result = ToolResult.ok(
        "hello",
        metadata=metadata,
    )

    metadata["changed"] = True

    assert result.metadata == {
        "source": "test",
    }


# ==========================================================
# Serialization
# ==========================================================


def test_tool_result_dict_success():

    result = ToolResult.ok(
        123
    )

    data = result.to_dict()

    assert data["success"] is True
    assert data["value"] == 123
    assert data["error"] is None
    assert data["metadata"] == {}
    assert isinstance(
        data["created_at"],
        str,
    )


def test_tool_result_dict_failure():

    result = ToolResult.fail(
        RuntimeError(
            "failed"
        )
    )

    data = result.to_dict()

    assert data["success"] is False
    assert data["value"] is None
    assert data["error"] == "failed"
    assert data["metadata"] == {}
    assert isinstance(
        data["created_at"],
        str,
    )


# ==========================================================
# Representation
# ==========================================================


def test_tool_result_repr_success():

    result = ToolResult.ok(
        "hello"
    )

    representation = repr(
        result
    )

    assert "ToolResult" in representation
    assert "success=True" in representation
    assert "hello" in representation


def test_tool_result_repr_failure():

    result = ToolResult.fail(
        RuntimeError(
            "failed"
        )
    )

    representation = repr(
        result
    )

    assert "ToolResult" in representation
    assert "success=False" in representation