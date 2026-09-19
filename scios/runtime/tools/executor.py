"""
SciOS Runtime Tool Executor
===========================

High-level orchestration layer for runtime tool execution.

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

from typing import Any

from .policy import ToolPolicy
from .registry import ToolRegistry
from .result import ToolResult
from .sandbox import ToolSandbox


__all__ = [
    "ToolExecutor",
]


# ==========================================================
# Tool Executor
# ==========================================================


class ToolExecutor:
    """
    Central runtime tool execution coordinator.

    Flow::

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
        # IMPORTANT:
        # Use explicit None checks rather than ``or``.
        #
        # ToolRegistry implements __len__(), therefore an empty
        # registry is falsy. Using ``registry or ToolRegistry()``
        # would silently replace an injected empty registry.

        self._registry = (
            registry
            if registry is not None
            else ToolRegistry()
        )

        self._policy = (
            policy
            if policy is not None
            else ToolPolicy()
        )

        self._sandbox = (
            sandbox
            if sandbox is not None
            else ToolSandbox(
                policy=self._policy
            )
        )

        # --------------------------------------------------
        # Execution statistics
        # --------------------------------------------------

        self._executions: int = 0
        self._success: int = 0
        self._failed: int = 0

    # ======================================================
    # Properties
    # ======================================================

    @property
    def registry(
        self,
    ) -> ToolRegistry:
        """Registered runtime tools."""

        return self._registry

    @property
    def policy(
        self,
    ) -> ToolPolicy:
        """Execution policy."""

        return self._policy

    @property
    def sandbox(
        self,
    ) -> ToolSandbox:
        """Execution sandbox."""

        return self._sandbox

    @property
    def executions(
        self,
    ) -> int:
        """Total execution attempts."""

        return self._executions

    @property
    def success(
        self,
    ) -> int:
        """Number of successful executions."""

        return self._success

    @property
    def failed(
        self,
    ) -> int:
        """Number of failed executions."""

        return self._failed

    # ======================================================
    # Internal Accounting
    # ======================================================

    def _record(
        self,
        result: ToolResult,
    ) -> ToolResult:
        """
        Update execution statistics.

        The execution counter is managed by the public
        execution entry points; this method only classifies
        the resulting ToolResult.
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
        Execute a registered tool by name.

        Example::

            executor.execute(
                "echo",
                value="hello",
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
        tool: Any,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Execute a tool instance through the sandbox.

        Raw sandbox results are normalized to ToolResult.
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
        Execute one registered tool multiple times.

        Each input mapping represents one execution.
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
        """Return registered tool names."""

        return self._registry.list()

    def has_tool(
        self,
        name: str,
    ) -> bool:
        """Return whether a tool is registered."""

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
        Initialize all registered tools.
        """

        for tool in self._registry:
            tool.initialize()

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown all registered tools.
        """

        for tool in self._registry:
            tool.shutdown()

    # ======================================================
    # Diagnostics
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """Return executor runtime status."""

        return {
            "executions": self._executions,
            "success": self._success,
            "failed": self._failed,
            "tools": self.available_tools(),
        }

    # ======================================================
    # Protocol
    # ======================================================

    def __len__(
        self,
    ) -> int:
        """Return total execution attempts."""

        return self._executions

    def __bool__(
        self,
    ) -> bool:
        """Return True after at least one execution."""

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