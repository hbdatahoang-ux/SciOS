from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID, uuid4

from scios.cognitive_core.tool.registry import ToolRegistry


@dataclass
class ToolAdapter:
    """
    ToolAdapter = Provides unified interface to call external tools.
    """

    adapter_id: UUID = field(default_factory=uuid4)
    registry: ToolRegistry = field(default_factory=ToolRegistry)

    # =========================================================
    # Core API
    # =========================================================

    def call_tool(self, name: str, inputs: Dict[str, Any]) -> Any:
        """
        Call a registered tool by name with given inputs.
        """
        handler = self.registry.get_tool(name)
        if not handler:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return handler(**inputs) if callable(handler) else handler

    def safe_call(self, name: str, inputs: Dict[str, Any]) -> Any:
        """
        Safe wrapper: call tool and catch errors.
        """
        try:
            return self.call_tool(name, inputs)
        except Exception as e:
            return {"error": str(e)}

    # =========================================================
    # Utility
    # =========================================================

    def available_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available tools from registry.
        """
        return self.registry.list_tools()
