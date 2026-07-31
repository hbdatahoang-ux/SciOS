"""
SciOS Runtime Agent ToolRouter Tests
====================================

Test ToolRouter integration with runtime tools.

Python 3.11+
"""


from scios.runtime.agent.tool_router import (
    ToolRouter,
)

from scios.runtime.tools.base import (
    Tool,
)

from scios.runtime.tools.result import (
    ToolResult,
)



# ==========================================================
# Mock Tool
# ==========================================================


class EchoTool(Tool):
    """
    Simple echo tool for routing tests.
    """


    NAME = "echo"


    DESCRIPTION = (
        "Return input text"
    )


    VERSION = (
        "1.0.0"
    )



    def execute(
        self,
        text: str,
    ) -> ToolResult:

        return ToolResult.ok(
            text
        )



# ==========================================================
# Register
# ==========================================================


def test_router_register():

    router = ToolRouter()


    tool = EchoTool()


    router.register(
        tool
    )


    assert "echo" in router.list_tools()

    assert router.has_tool(
        "echo"
    )



    assert router.resolve(
        "echo"
    ) is tool



# ==========================================================
# Execute
# ==========================================================


def test_router_execute():

    router = ToolRouter()


    router.register(
        EchoTool()
    )


    result = router.route(
        "echo",
        text="hello",
    )


    assert isinstance(
        result,
        ToolResult,
    )


    assert result.success is True


    assert result.value == (
        "hello"
    )



# ==========================================================
# Missing Tool
# ==========================================================


def test_router_missing_tool():

    router = ToolRouter()


    result = router.route(
        "unknown",
    )


    assert isinstance(
        result,
        ToolResult,
    )


    assert result.success is False



# ==========================================================
# Callable API
# ==========================================================


def test_router_callable():

    router = ToolRouter()


    router.register(
        EchoTool()
    )


    result = router(
        "echo",
        text="scios",
    )


    assert result.value == (
        "scios"
    )



# ==========================================================
# Diagnostics
# ==========================================================


def test_router_status():

    router = ToolRouter()


    router.register(
        EchoTool()
    )


    status = router.status()


    assert status["count"] == 1

    assert "echo" in status["tools"]