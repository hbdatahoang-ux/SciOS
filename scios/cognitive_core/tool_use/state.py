# scios/cognitive_core/tool_use/state.py

"""
SciOS Tool State
================

Quản lý trạng thái của tool trong pipeline:
- Trạng thái hiện tại (idle, running, success, error)
- Request/Response gần nhất
- Metadata
"""

from typing import Dict, Any, Optional


class ToolState:
    """
    ToolState lưu giữ trạng thái hiện tại của tool.
    """

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        self.status: str = "idle"  # idle, running, success, error
        self.last_request: Optional[Dict[str, Any]] = None
        self.last_response: Optional[Dict[str, Any]] = None
        self.metadata: Dict[str, Any] = {}

    def set_running(self, request: Dict[str, Any]) -> None:
        """
        Đặt trạng thái tool thành running.
        """
        self.status = "running"
        self.last_request = request

    def set_success(self, response: Dict[str, Any]) -> None:
        """
        Đặt trạng thái tool thành success.
        """
        self.status = "success"
        self.last_response = response

    def set_error(self, response: Dict[str, Any]) -> None:
        """
        Đặt trạng thái tool thành error.
        """
        self.status = "error"
        self.last_response = response

    def reset(self) -> None:
        """
        Reset trạng thái tool về idle.
        """
        self.status = "idle"
        self.last_request = None
        self.last_response = None
        self.metadata.clear()

    def to_dict(self) -> Dict[str, Any]:
        """
        Xuất trạng thái tool thành dict.
        """
        return {
            "tool": self.tool_name,
            "status": self.status,
            "last_request": self.last_request,
            "last_response": self.last_response,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"<ToolState tool={self.tool_name} status={self.status}>"
