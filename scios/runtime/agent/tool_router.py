"""
SciOS Runtime Agent Tool Router
===============================

Agent-facing tool dispatch layer.

Responsibilities
-----------------
- Resolve tools from registry
- Route execution requests
- Coordinate ToolExecutor
- Normalize ToolResult
- Batch execution
- Runtime diagnostics

Architecture
------------

Agent
 |
ToolRouter
 |
ToolRegistry
 |
ToolExecutor
 |
ToolSandbox
 |
Tool
 |
ToolResult


Python 3.11+
"""

from __future__ import annotations


from typing import (
    Any,
)


from scios.runtime.tools.registry import (
    ToolRegistry,
)

from scios.runtime.tools.executor import (
    ToolExecutor,
)

from scios.runtime.tools.result import (
    ToolResult,
)



__all__ = [
    "ToolRouter",
]



# ==========================================================
# Tool Router
# ==========================================================


class ToolRouter:
    """
    Agent tool routing coordinator.

    Example
    -------

    router = ToolRouter()

    router.register(
        EchoTool()
    )

    result = router.route(
        "echo",
        text="hello",
    )
    """



    # ======================================================
    # Construction
    # ======================================================


    def __init__(
        self,
        *,
        registry: ToolRegistry | None = None,
        executor: ToolExecutor | None = None,
    ) -> None:


        self._registry = (
            registry
            or ToolRegistry()
        )


        self._executor = (
            executor
            or ToolExecutor()
        )


        self._executions = 0



    # ======================================================
    # Properties
    # ======================================================


    @property
    def registry(
        self,
    ) -> ToolRegistry:

        return self._registry



    @property
    def executor(
        self,
    ) -> ToolExecutor:

        return self._executor



    @property
    def executions(
        self,
    ) -> int:

        return self._executions



    # ======================================================
    # Registration
    # ======================================================


    def register(
        self,
        tool,
    ):
        """
        Register runtime tool.
        """

        return self._registry.register(
            tool
        )



    def unregister(
        self,
        name: str,
    ) -> bool:
        """
        Remove tool.
        """

        return self._registry.unregister(
            name
        )



    def list_tools(
        self,
    ) -> list[str]:
        """
        List registered tools.
        """

        return self._registry.list()



    def has_tool(
        self,
        name: str,
    ) -> bool:

        return (
            self._registry.get(name)
            is not None
        )



    # ======================================================
    # Resolve
    # ======================================================


    def resolve(
        self,
        name: str,
    ):
        """
        Resolve tool by name.
        """


        tool = self._registry.get(
            name
        )


        if tool is None:

            raise ValueError(
                f"Tool not found: {name}"
            )


        return tool



    # ======================================================
    # Execute Route
    # ======================================================


    def route(
        self,
        name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Route execution request.

        Agent
          |
        ToolRouter
          |
        ToolExecutor
          |
        ToolResult
        """

        try:

            tool = self.resolve(
                name
            )


            result = self._executor.execute_tool(
                tool,
                **kwargs,
            )


            self._executions += 1



            if isinstance(
                result,
                ToolResult,
            ):

                return result



            return ToolResult.ok(
                result
            )



        except Exception as exc:


            self._executions += 1


            return ToolResult.fail(
                exc
            )



    # ======================================================
    # Batch Execution
    # ======================================================


    def route_many(
        self,
        requests: list[dict[str, Any]],
    ) -> list[ToolResult]:
        """
        Execute multiple tool requests.


        Example:

        [
            {
                "name": "echo",
                "args": {
                    "text": "hello"
                }
            }
        ]
        """


        results: list[ToolResult] = []


        for request in requests:


            name = request.get(
                "name"
            )


            args = request.get(
                "args",
                {},
            )


            if name is None:


                results.append(
                    ToolResult.fail(
                        ValueError(
                            "Missing tool name"
                        )
                    )
                )


                continue



            results.append(
                self.route(
                    name,
                    **args,
                )
            )


        return results



    # ======================================================
    # Callable API
    # ======================================================


    def __call__(
        self,
        name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Shortcut:

            router(
                "echo",
                text="hello"
            )
        """

        return self.route(
            name,
            **kwargs,
        )



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "tools":
                self.list_tools(),


            "count":
                len(
                    self._registry
                ),


            "executions":
                self._executions,

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return len(
            self._registry
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.has_tool(
            name
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "ToolRouter("
            f"tools={len(self)}, "
            f"executions={self._executions}"
            ")"
        )