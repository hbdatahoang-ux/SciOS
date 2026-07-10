"""
SciOS Cognitive Stage
=====================

Abstract base class cho mọi stage trong CognitivePipeline.
Stage chỉ cần implement `run(context)` và có thể override `reset()`.
"""

from abc import ABC, abstractmethod
from typing import Any
from .context import CognitiveContext


class CognitiveStage(ABC):
    """
    Abstract CognitiveStage.
    Mọi stage (Perception, Memory, Reasoning, Planner, ToolUse, Reflection, ...)
    đều kế thừa từ đây.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.status: str = "idle"
        self.message: str | None = None

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    @abstractmethod
    def run(self, context: CognitiveContext) -> Any:
        """
        Thực thi stage với CognitiveContext.
        Mỗi stage sẽ đọc/ghi dữ liệu vào context.
        """
        ...

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------

    def reset(self) -> None:
        """Đặt lại trạng thái stage."""
        self.status = "idle"
        self.message = None

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
        }

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<CognitiveStage name={self.name} status={self.status}>"
