# tests/cognitive_core/tool_use/test_selector.py

from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.selector import ToolSelector


def test_selector_selects_known_tool_from_request():
    selector = ToolSelector(["calculator", "echo"])

    request = ToolRequest(
        tool="calculator",
        action="evaluate",
        params={"expression": "2+2"},
    )

    assert selector.select(request) == "calculator"


def test_selector_selects_known_tool_from_mapping():
    selector = ToolSelector(["calculator", "echo"])

    request = {
        "tool": "echo",
        "action": "say",
        "params": {"message": "hello"},
    }

    assert selector.select(request) == "echo"


def test_selector_returns_none_for_unknown_tool():
    selector = ToolSelector(["calculator", "echo"])

    request = ToolRequest(
        tool="filesystem",
        action="read",
    )

    assert selector.select(request) is None


def test_selector_accepts_any_tool_when_capabilities_are_unrestricted():
    selector = ToolSelector()

    request = ToolRequest(
        tool="calculator",
        action="evaluate",
    )

    assert selector.select(request) == "calculator"


def test_selector_returns_none_for_invalid_mapping():
    selector = ToolSelector(["calculator"])

    assert selector.select({}) is None
    assert selector.select({"tool": ""}) is None
    assert selector.select({"tool": "   "}) is None


def test_selector_returns_none_for_invalid_request_type():
    selector = ToolSelector(["calculator"])

    assert selector.select(None) is None
    assert selector.select(42) is None


def test_selector_available_tools():
    selector = ToolSelector(["calculator", "echo"])

    assert selector.available_tools() == ("calculator", "echo")


def test_selector_has_known_tool():
    selector = ToolSelector(["calculator", "echo"])

    assert selector.has("calculator")
    assert selector.has("echo")
    assert not selector.has("filesystem")


def test_selector_unrestricted_has_any_nonempty_tool():
    selector = ToolSelector()

    assert selector.has("calculator")
    assert selector.has("filesystem")
    assert not selector.has("")
    assert not selector.has("   ")


def test_selector_membership():
    selector = ToolSelector(["calculator", "echo"])

    assert "calculator" in selector
    assert "filesystem" not in selector


def test_selector_request_factory():
    selector = ToolSelector()

    request = selector.request(
        "calculator",
        "evaluate",
        params={"expression": "2+2"},
        metadata={"source": "planner"},
    )

    assert isinstance(request, ToolRequest)
    assert request.tool == "calculator"
    assert request.action == "evaluate"
    assert request.params == {"expression": "2+2"}
    assert request.metadata == {"source": "planner"}


def test_selector_accepts_capability_mapping():
    selector = ToolSelector(
        {
            "calculator": {"description": "evaluate expressions"},
            "echo": {"description": "echo input"},
        }
    )

    assert selector.available_tools() == ("calculator", "echo")
    assert selector.has("calculator")
    assert selector.select(
        ToolRequest(tool="echo", action="say")
    ) == "echo"


def test_selector_strips_tool_name():
    selector = ToolSelector(["calculator"])

    request = {
        "tool": "  calculator  ",
        "action": "evaluate",
    }

    assert selector.select(request) == "calculator"


def test_selector_repr():
    selector = ToolSelector(["calculator", "echo"])

    representation = repr(selector)

    assert "ToolSelector" in representation
    assert "2" in representation
