"""
SciOS Runtime Tool Executor
===========================

High-level orchestration layer
for runtime tool execution.

Responsibilities
-----------------
- Resolve tools
- Execute tools
- Coordinate sandbox
- Enforce policy
- Collect statistics
- Lifecycle management

Python 3.11+
"""

from __future__ import annotations


from typing import (
    Any,
)


from .registry import ToolRegistry

from .sandbox import ToolSandbox

from .policy import ToolPolicy

from .result import ToolResult



__all__ = [
    "ToolExecutor",
]



# ==========================================================
# Tool Executor
# ==========================================================


class ToolExecutor:
    """
    Central runtime tool execution coordinator.


    Flow:

        ToolRouter
             |
        ToolExecutor
             |
        ToolSandbox
             |
        Tool
             |
        ToolResult
    """



    # ======================================================
    # Construction
    # ======================================================


    def __init__(
        self,
        *,
        registry: ToolRegistry | None = None,
        policy: ToolPolicy | None = None,
        sandbox: ToolSandbox | None = None,
    ) -> None:


        self._registry = (
            registry
            or ToolRegistry()
        )


        self._policy = (
            policy
            or ToolPolicy()
        )


        self._sandbox = (
            sandbox
            or ToolSandbox(
                policy=self._policy
            )
        )


        # statistics

        self._executions = 0

        self._success = 0

        self._failed = 0



    # ======================================================
    # Properties
    # ======================================================


    @property
    def registry(
        self,
    ) -> ToolRegistry:

        return self._registry



    @property
    def policy(
        self,
    ) -> ToolPolicy:

        return self._policy



    @property
    def sandbox(
        self,
    ) -> ToolSandbox:

        return self._sandbox



    @property
    def executions(
        self,
    ) -> int:

        return self._executions



    @property
    def success(
        self,
    ) -> int:

        return self._success



    @property
    def failed(
        self,
    ) -> int:

        return self._failed



    # ======================================================
    # Internal accounting
    # ======================================================


    def _record(
        self,
        result: ToolResult,
    ) -> ToolResult:
        """
        Update execution statistics.
        """

        if result.success:

            self._success += 1

        else:

            self._failed += 1


        return result



    # ======================================================
    # Execute By Name
    # ======================================================


    def execute(
        self,
        name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute registered tool by name.


        Example:

            executor.execute(
                "echo",
                text="hello"
            )
        """


        tool = self._registry.get(
            name
        )


        if tool is None:

            self._executions += 1


            return self._record(
                ToolResult.fail(
                    KeyError(
                        f"Unknown tool: {name}"
                    )
                )
            )


        return self.execute_tool(
            tool,
            **kwargs,
        )



    # ======================================================
    # Execute Tool Instance
    # ======================================================


    def execute_tool(
        self,
        tool,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute Tool instance directly.
        """


        self._executions += 1


        try:

            result = self._sandbox.execute(
                tool,
                **kwargs,
            )


            if not isinstance(
                result,
                ToolResult,
            ):

                result = ToolResult.ok(
                    result
                )


            return self._record(
                result
            )



        except Exception as exc:


            return self._record(
                ToolResult.fail(
                    exc
                )
            )



    # ======================================================
    # Batch Execution
    # ======================================================


    def execute_many(
        self,
        name: str,
        inputs: list[dict[str, Any]],
    ) -> list[ToolResult]:
        """
        Execute one tool many times.
        """


        results: list[ToolResult] = []


        for params in inputs:

            results.append(
                self.execute(
                    name,
                    **params,
                )
            )


        return results



    # ======================================================
    # Discovery
    # ======================================================


    def available_tools(
        self,
    ) -> list[str]:

        return self._registry.list()



    def has_tool(
        self,
        name: str,
    ) -> bool:

        return self._registry.exists(
            name
        )



    # ======================================================
    # Lifecycle
    # ======================================================


    def initialize(
        self,
    ) -> None:
        """
        Initialize all tools.
        """


        for tool in self._registry:

            tool.initialize()



    def shutdown(
        self,
    ) -> None:
        """
        Shutdown tools.
        """


        for tool in self._registry:

            tool.shutdown()



    # ======================================================
    # Diagnostics
    # ======================================================


    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "executions":
                self._executions,


            "success":
                self._success,


            "failed":
                self._failed,


            "tools":
                self.available_tools(),

        }



    # ======================================================
    # Protocol
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return self._executions



    def __bool__(
        self,
    ) -> bool:

        return self._executions > 0



    def __repr__(
        self,
    ) -> str:

        return (
            "ToolExecutor("
            f"executions={self._executions}, "
            f"success={self._success}, "
            f"failed={self._failed}"
            ")"
        )