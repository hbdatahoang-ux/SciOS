"""
ToolExecutor tests
"""


from scios.runtime.tools import (
    ToolExecutor,
    ToolRegistry,
    ToolSandbox,
    ToolPolicy,
    Tool,
)



class EchoTool(Tool):

    name = "echo"


    def execute(
        self,
        value,
    ):

        return value




def test_executor_run():

    registry = ToolRegistry()


    registry.register(
        EchoTool()
    )


    executor = ToolExecutor(
        registry=registry,
        sandbox=ToolSandbox(),
        policy=ToolPolicy(),
    )


    result = executor.execute(
        "echo",
        value="hello",
    )


    assert result.value == "hello"