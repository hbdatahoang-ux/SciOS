"""
ToolResult tests
"""

from scios.runtime.tools import ToolResult



def test_tool_result_success():

    result = ToolResult.ok(
        "hello"
    )

    assert result.success is True
    assert result.value == "hello"



def test_tool_result_failure():

    error = RuntimeError(
        "failed"
    )

    result = ToolResult.fail(
        error
    )


    assert result.success is False
    assert result.error == error



def test_tool_result_dict():

    result = ToolResult.ok(
        123
    )


    data = result.to_dict()


    assert data["success"] is True
    assert data["value"] == 123