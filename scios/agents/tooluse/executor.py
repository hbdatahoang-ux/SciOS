"""
SciOS Tool Executor

Executes tools after dispatch.
"""

from typing import Any, Dict

from .tool import Tool


class ToolExecutor:
    """
    Executes a tool instance.

    Responsibilities
    ----------------
    - Execute tool
    - Capture execution result
    - Handle execution errors
    - Provide execution metadata
    """

    def execute(
        self,
        tool: Tool,
        *args,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute a tool.
        """

        try:

            result = tool.execute(
                *args,
                **kwargs,
            )

            return {
                "success": True,
                "tool": tool.name,
                "result": result,
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": tool.name,
                "error": str(exc),
            }

    def status(self):
        """
        Executor status.
        """

        return {
            "component": "ToolExecutor",
            "status": "ready",
        }
