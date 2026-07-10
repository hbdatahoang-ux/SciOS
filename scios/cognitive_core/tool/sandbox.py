from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID, uuid4

from scios.cognitive_core.tool.registry import ToolRegistry
from scios.cognitive_core.tool.adapter import ToolAdapter


@dataclass
class ToolSandbox:
    """
    ToolSandbox = Safe environment to test external tools.
    """

    sandbox_id: UUID = field(default_factory=uuid4)
    registry: ToolRegistry = field(default_factory=ToolRegistry)
    adapter: ToolAdapter = field(init=False)

    def __post_init__(self):
        self.adapter = ToolAdapter(registry=self.registry)

    # =========================================================
    # Core API
    # =========================================================

    def test_tool(self, name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a tool in sandbox mode and capture result.
        """
        result = self.adapter.safe_call(name, inputs)
        return {
            "tool": name,
            "inputs": inputs,
            "result": result,
            "status": "success" if "error" not in result else "failed"
        }

    def register_and_test(self, name: str, handler: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a tool temporarily and test it immediately.
        """
        self.registry.register_tool(name, handler)
        return self.test_tool(name, inputs)

    # =========================================================
    # Utility
    # =========================================================

    def clear_sandbox(self) -> None:
        """
        Clear all registered tools in sandbox.
        """
        self.registry.tools.clear()
