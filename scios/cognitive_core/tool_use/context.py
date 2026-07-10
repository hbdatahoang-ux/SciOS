# scios/cognitive_core/tool_use/context.py

"""
SciOS Tool Context
==================

Lưu giữ ngữ cảnh thực thi tool:
- User, session, pipeline state
- Request và metadata
"""

from typing import Any, Dict, Optional


class ToolContext:
    """
    ToolContext chứa toàn bộ thông tin cần thiết để thực thi tool.
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        pipeline_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.pipeline_state = pipeline_state or {}
        self.metadata = metadata or {}

    def set(self, key: str, value: Any) -> None:
        """
        Đặt giá trị vào context.
        """
        self.metadata[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Lấy giá trị từ context.
        """
        return self.metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """
        Xuất toàn bộ context thành dict.
        """
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "pipeline_state": self.pipeline_state,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"<ToolContext user={self.user_id} session={self.session_id}>"
