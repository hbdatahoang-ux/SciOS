"""
SciOS Runtime Tool Executor
===========================

High-level orchestration layer
for runtime tool execution.

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
    Central tool execution coordinator.

    Responsibilities:

    - resolve tools
    - enforce policy
    - execute in sandbox
    - collect statistics
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



    # ======================================================
    # Execute
    # ======================================================


    def execute(
        self,
        name: str,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute tool by name.
        """


        tool = self._registry.get(
            name
        )


        if tool is None:

            self._failed += 1


            return ToolResult.fail(
                KeyError(
                    f"Unknown tool: {name}"
                )
            )



        self._executions += 1



        result = self._sandbox.execute(
            tool,
            **kwargs,
        )



        if result.success:

            self._success += 1

        else:

            self._failed += 1



        return result



    # ======================================================
    # Direct Execute
    # ======================================================


    def execute_tool(
        self,
        tool,
        **kwargs,
    ) -> ToolResult:
        """
        Execute Tool instance directly.
        """


        self._executions += 1


        result = self._sandbox.execute(
            tool,
            **kwargs,
        )


        if result.success:

            self._success += 1

        else:

            self._failed += 1



        return result



    # ======================================================
    # Batch
    # ======================================================


    def execute_many(
        self,
        name: str,
        inputs: list[dict[str, Any]],
    ) -> list[ToolResult]:
        """
        Execute same tool multiple times.
        """


        return [

            self.execute(
                name,
                **params,
            )

            for params in inputs

        ]



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

        for tool in self._registry:

            tool.initialize()



    def shutdown(
        self,
    ) -> None:

        self._registry.clear()



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



    def __repr__(
        self,
    ) -> str:

        return (
            "ToolExecutor("
            f"executions={self._executions}"
            ")"
        )