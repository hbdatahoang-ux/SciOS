# scios/cognitive_core/tool_use/history.py

"""
SciOS Tool History
==================

Lưu giữ nhật ký các lần gọi tool:
- Request
- Response
- Thời gian
- Trạng thái
"""

import time
from typing import Any, Dict, List


class ToolHistoryEntry:
    """
    Một entry trong ToolHistory: lưu request, response, timestamp.
    """

    def __init__(self, tool: str, request: Dict[str, Any], response: Dict[str, Any]) -> None:
        self.tool = tool
        self.request = request
        self.response = response
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "request": self.request,
            "response": self.response,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        status = self.response.get("status", "unknown")
        return f"<ToolHistoryEntry tool={self.tool} status={status} at={self.timestamp}>"



class ToolHistory:
    """
    ToolHistory quản lý danh sách các entry.
    """

    def __init__(self) -> None:
        self.entries: List[ToolHistoryEntry] = []

    def log(self, tool: str, request: Dict[str, Any], response: Dict[str, Any]) -> None:
        """
        Ghi lại một lần gọi tool.
        """
        entry = ToolHistoryEntry(tool, request, response)
        self.entries.append(entry)

    def list(self) -> List[Dict[str, Any]]:
        """
        Liệt kê toàn bộ lịch sử dưới dạng dict.
        """
        return [entry.to_dict() for entry in self.entries]

    def filter_by_tool(self, tool: str) -> List[Dict[str, Any]]:
        """
        Lọc lịch sử theo tên tool.
        """
        return [entry.to_dict() for entry in self.entries if entry.tool == tool]

    def clear(self) -> None:
        """
        Xóa toàn bộ lịch sử.
        """
        self.entries.clear()

    def __repr__(self) -> str:
        return f"<ToolHistory entries={len(self.entries)}>"
