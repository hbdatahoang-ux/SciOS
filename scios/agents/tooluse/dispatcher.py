"""
SciOS Tool Dispatcher

Dispatches execution requests to registered tools.
"""

from typing import Any, Dict

from .registry import ToolRegistry


class ToolDispatcher:
    """
    Tool execution dispatcher.

    Responsibilities
    ----------------
    - Lookup tools
    - Execute tools
    - Capture execution results
    """

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def dispatch(
        self,
        tool_name: str,
        *args,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute a registered tool.
        """

        tool = self.registry.get(tool_name)

        if tool is None:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Tool '{tool_name}' not found.",
            }

        try:

            result = tool.execute(
                *args,
                **kwargs,
            )

            return {
                "success": True,
                "tool": tool_name,
                "result": result,
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": tool_name,
                "error": str(exc),
            }

    def available_tools(self):
        """
        Return registered tool names.
        """
        return self.registry.list_tools()

    def status(self):
        """
        Dispatcher status.
        """
        return {
            "component": "ToolDispatcher",
            "registered_tools": self.registry.count(),
        }
