# scios/cognitive_core/tool_use/response.py

"""
SciOS Tool Response
===================

Chuẩn hóa kết quả trả về từ tool:
- Status (success/error)
- Tool name
- Result hoặc message
- Metadata
"""

from typing import Dict, Any, Optional


class ToolResponse:
    """
    ToolResponse là cấu trúc chuẩn cho mọi kết quả trả về từ tool.
    """

    def __init__(
        self,
        status: str,
        tool: Optional[str] = None,
        result: Optional[Any] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status = status
        self.tool = tool
        self.result = result
        self.message = message
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Xuất ToolResponse thành dict để pipeline xử lý tiếp.
        """
        return {
            "status": self.status,
            "tool": self.tool,
            "result": self.result,
            "message": self.message,
            "metadata": self.metadata,
        }

    @classmethod
    def success(cls, tool: str, result: Any, metadata: Optional[Dict[str, Any]] = None) -> "ToolResponse":
        """
        Tạo response thành công.
        """
        return cls(status="success", tool=tool, result=result, metadata=metadata)

    @classmethod
    def error(cls, tool: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> "ToolResponse":
        """
        Tạo response lỗi.
        """
        return cls(status="error", tool=tool, message=message, metadata=metadata)

    def __repr__(self) -> str:
        return f"<ToolResponse status={self.status} tool={self.tool}>"
