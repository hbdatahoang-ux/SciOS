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

from typing import Any

from scios.runtime.tools.base import Tool
from scios.runtime.tools.executor import ToolExecutor
from scios.runtime.tools.registry import ToolRegistry
from scios.runtime.tools.result import ToolResult


__all__ = [
    "ToolRouter",
]


# ==========================================================
# Tool Router
# ==========================================================


class ToolRouter:
    """
    Agent-facing tool routing coordinator.
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

        # IMPORTANT:
        # ToolRegistry implements __len__(), therefore an empty
        # registry is falsy. Never use ``registry or ...``.

        self._registry = (
            registry
            if registry is not None
            else ToolRegistry()
        )

        self._executor = (
            executor
            if executor is not None
            else ToolExecutor()
        )

        self._executions: int = 0

    # ======================================================
    # Properties
    # ======================================================

    @property
    def registry(
        self,
    ) -> ToolRegistry:
        """Underlying tool registry."""

        return self._registry

    @property
    def executor(
        self,
    ) -> ToolExecutor:
        """Underlying tool executor."""

        return self._executor

    @property
    def executions(
        self,
    ) -> int:
        """Number of routing attempts."""

        return self._executions

    # ======================================================
    # Registration
    # ======================================================

    def register(
        self,
        tool: Tool,
    ) -> Tool:
        """Register a runtime tool."""

        return self._registry.register(
            tool
        )

    def unregister(
        self,
        name: str,
    ) -> Tool | None:
        """Remove a runtime tool."""

        return self._registry.unregister(
            name
        )

    def list_tools(
        self,
    ) -> list[str]:
        """Return registered tool names."""

        return self._registry.list()

    def has_tool(
        self,
        name: str,
    ) -> bool:
        """Return whether a tool exists."""

        return self._registry.exists(
            name
        )

    # ======================================================
    # Resolve
    # ======================================================

    def resolve(
        self,
        name: str,
    ) -> Tool:
        """
        Resolve a registered tool.

        Raises
        ------
        ValueError
            If the tool is not registered.
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
        Route an execution request through ToolExecutor.

        Router does not execute tools directly.
        """

        self._executions += 1

        try:
            tool = self.resolve(
                name
            )

            result = self._executor.execute_tool(
                tool,
                **kwargs,
            )

            if isinstance(
                result,
                ToolResult,
            ):
                return result

            return ToolResult.ok(
                result
            )

        except Exception as exc:
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
        Route multiple tool requests.

        Request format::

            {
                "name": "echo",
                "args": {
                    "text": "hello"
                }
            }
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

            if not isinstance(
                args,
                dict,
            ):
                results.append(
                    ToolResult.fail(
                        TypeError(
                            "Tool args must be a dict"
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
        """Shortcut for route()."""

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
        """Return router runtime status."""

        return {
            "tools": self.list_tools(),
            "count": len(self._registry),
            "executions": self._executions,
        }

    # ======================================================
    # Protocol
    # ======================================================

    def __len__(
        self,
    ) -> int:
        """Return number of registered tools."""

        return len(
            self._registry
        )

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """Support ``name in router``."""

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