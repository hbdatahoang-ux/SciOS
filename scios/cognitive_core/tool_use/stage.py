"""
SciOS Tool Stage
================

Represents the lifecycle state of Tool Use.
"""

from __future__ import annotations
from typing import Optional, Dict


class ToolStage:
    """
    Represents execution state for Tool Use.

    Lifecycle states:
    - idle: chưa bắt đầu
    - running: đang thực thi
    - success: hoàn tất thành công
    - error: gặp lỗi
    """

    def __init__(self) -> None:
        self.reset()

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(self, message: Optional[str] = None) -> None:
        """Đặt trạng thái sang 'running'."""
        self.status = "running"
        self.message = message

    def complete(self, message: Optional[str] = None) -> None:
        """Đặt trạng thái sang 'success'."""
        self.status = "success"
        self.message = message

    def error(self, message: Optional[str] = None) -> None:
        """Đặt trạng thái sang 'error'."""
        self.status = "error"
        self.message = message

    def reset(self) -> None:
        """Đặt lại trạng thái về 'idle'."""
        self.status = "idle"
        self.message = None

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Xuất trạng thái stage dưới dạng dict."""
        return {
            "status": self.status,
            "message": self.message,
        }

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(self) -> str:
        return f"<ToolStage status={self.status} message={self.message}>"

# ---------------------------------------------------------------------
# Backward compatibility alias
# ---------------------------------------------------------------------

ToolUseStage = ToolStage
