"""
ToolRegistry tests
"""


from scios.runtime.tools import (
    Tool,
    ToolRegistry,
)



class EchoTool(Tool):

    name = "echo"


    def execute(
        self,
        value,
    ):

        return value




def test_register_tool():

    registry = ToolRegistry()


    tool = EchoTool()


    registry.register(
        tool
    )


    assert registry.exists(
        "echo"
    )



def test_get_tool():

    registry = ToolRegistry()


    tool = EchoTool()


    registry.register(
        tool
    )


    loaded = registry.get(
        "echo"
    )


    assert loaded is tool



def test_unregister():

    registry = ToolRegistry()


    registry.register(
        EchoTool()
    )


    registry.unregister(
        "echo"
    )


    assert not registry.exists(
        "echo"
    )