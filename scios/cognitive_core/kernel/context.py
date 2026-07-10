"""
SciOS Cognitive Context
=======================

CognitiveContext là bộ nhớ tạm xuyên suốt pipeline.
Mọi stage đều đọc/ghi dữ liệu vào đây.
"""

from typing import Any, Dict, List
from .request import CognitiveRequest


class CognitiveContext:
    """
    CognitiveContext lưu trữ trạng thái của toàn bộ pipeline.
    """

    def __init__(self, request: CognitiveRequest) -> None:
        self.request = request
        self.state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.trace: List[Dict[str, Any]] = []

    # -----------------------------------------------------
    # State management
    # -----------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        """Ghi kết quả của một stage vào context."""
        self.state[key] = value
        self.trace.append({key: value})

    def get(self, key: str) -> Any:
        """Đọc kết quả của một stage từ context."""
        return self.state.get(key)

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "state": self.state,
            "metadata": self.metadata,
            "trace": self.trace,
        }

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<CognitiveContext state_keys={list(self.state.keys())}>"
