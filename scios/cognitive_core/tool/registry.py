from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass
class ToolRegistry:
    """
    ToolRegistry = Manages external tool registration and lookup.
    """

    registry_id: UUID = field(default_factory=uuid4)
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # =========================================================
    # Core API
    # =========================================================

    def register_tool(self, name: str, handler: Any, metadata: Dict[str, Any] | None = None) -> None:
        """
        Register a new tool with handler and optional metadata.
        """
        self.tools[name] = {
            "handler": handler,
            "metadata": metadata or {}
        }

    def get_tool(self, name: str) -> Any:
        """
        Retrieve tool handler by name.
        """
        tool = self.tools.get(name)
        return tool["handler"] if tool else None

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Return all registered tools with metadata.
        """
        return dict(self.tools)

    def unregister_tool(self, name: str) -> None:
        """
        Remove a tool from registry.
        """
        if name in self.tools:
            del self.tools[name]

    # =========================================================
    # Utility
    # =========================================================

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.
        """
        return name in self.tools
