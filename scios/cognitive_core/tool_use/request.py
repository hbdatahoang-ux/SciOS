# scios/cognitive_core/tool_use/request.py

"""
SciOS Tool Request
==================

Chuẩn hóa yêu cầu gọi tool:
- Tool name
- Action/operation
- Parameters
- Metadata
"""

from typing import Dict, Any, Optional


class ToolRequest:
    """
    ToolRequest là cấu trúc chuẩn cho mọi yêu cầu gọi tool.
    """

    def __init__(
        self,
        tool: str,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.tool = tool
        self.action = action
        self.params = params or {}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Xuất ToolRequest thành dict để truyền qua pipeline.
        """
        return {
            "tool": self.tool,
            "action": self.action,
            "params": self.params,
            "metadata": self.metadata,
        }

    @classmethod
    def from_context(cls, context: Dict[str, Any]) -> "ToolRequest":
        """
        Tạo ToolRequest từ context pipeline.
        """
        return cls(
            tool=context.get("tool"),
            action=context.get("action") or context.get("operation"),
            params=context.get("params", {}),
            metadata=context.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return f"<ToolRequest tool={self.tool} action={self.action}>"
