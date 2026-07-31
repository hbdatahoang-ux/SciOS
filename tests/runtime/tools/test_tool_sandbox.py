"""
ToolSandbox tests
"""


from scios.runtime.tools import (
    ToolSandbox,
)



def test_sandbox_execute():

    sandbox = ToolSandbox()


    result = sandbox.execute(
        lambda: "ok"
    )


    assert result == "ok"