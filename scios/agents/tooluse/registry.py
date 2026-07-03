"""
SciOS Tool Registry

Central registry for all executable tools.
"""

from typing import Dict, List, Optional

from .tool import Tool


class ToolRegistry:
    """
    Registry for SciOS tools.

    Responsibilities
    ----------------
    - Register tools
    - Remove tools
    - Lookup tools
    - List available tools
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """
        Register a tool.
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str):
        """
        Remove a tool.
        """
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        """
        Retrieve a tool by name.
        """
        return self._tools.get(name)

    def exists(self, name: str) -> bool:
        """
        Check if a tool exists.
        """
        return name in self._tools

    def list_tools(self) -> List[str]:
        """
        Return registered tool names.
        """
        return sorted(self._tools.keys())

    def metadata(self):
        """
        Return metadata for all tools.
        """
        return {
            name: tool.metadata()
            for name, tool in self._tools.items()
        }

    def clear(self):
        """
        Remove all tools.
        """
        self._tools.clear()

    def count(self) -> int:
        """
        Number of registered tools.
        """
        return len(self._tools)

    def status(self):
        """
        Registry status.
        """
        return {
            "registered_tools": self.count(),
            "tools": self.list_tools(),
        }