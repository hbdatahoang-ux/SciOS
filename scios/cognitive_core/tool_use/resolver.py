# scios/cognitive_core/tool_use/resolver.py

"""
SciOS Tool Resolver
===================

Xác định tool phù hợp từ registry dựa trên request.
"""

from typing import Dict, Any, Optional
from scios.cognitive_core.tool_use.registry import ToolRegistry
from scios.cognitive_core.tool_use.base import Tool


class ToolResolver:
    """
    ToolResolver chịu trách nhiệm chọn tool phù hợp từ registry.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def resolve(self, request: Dict[str, Any]) -> Optional[Tool]:
        """
        Phân tích request để chọn tool phù hợp.
        - Nếu request có key 'tool', dùng trực tiếp.
        - Nếu không, thử suy luận từ nội dung task.
        """
        tool_name = request.get("tool")

        if tool_name:
            return self.registry.get(tool_name)

        # Nếu không có 'tool', thử suy luận từ task
        task = request.get("task", "")
        if isinstance(task, str):
            if task.lower().startswith("calculate"):
                return self.registry.get("calculator")
            elif "file" in task.lower():
                return self.registry.get("filesystem")
            elif "http" in task.lower() or "url" in task.lower():
                return self.registry.get("web")

        return None
