# scios/cognitive_core/tool_use/registry.py

"""
SciOS Tool Registry
===================

Quản lý việc đăng ký và tra cứu các Tool trong hệ thống.
"""

from typing import Dict, Optional
from scios.cognitive_core.tool_use.base import Tool


class ToolRegistry:
    """
    ToolRegistry lưu trữ và quản lý các Tool đã đăng ký.
    """

    def __init__(self) -> None:
        # Dùng dict để ánh xạ tên tool -> instance
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Đăng ký một tool mới vào registry.
        Nếu tên đã tồn tại, sẽ ghi đè.
        """
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """
        Xóa một tool khỏi registry theo tên.
        """
        if name in self._tools:
            del self._tools[name]

    def get(self, name: str) -> Optional[Tool]:
        """
        Lấy tool theo tên. Trả về None nếu không tìm thấy.
        """
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """
        Liệt kê tất cả tool đã đăng ký cùng mô tả.
        """
        return {name: tool.description for name, tool in self._tools.items()}

    def __repr__(self) -> str:
        return f"<ToolRegistry tools={list(self._tools.keys())}>"
