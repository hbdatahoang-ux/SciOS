"""
SciOS Stage Registry
====================

Quản lý stage trong CognitivePipeline.
Cho phép đăng ký, xoá, truy vấn, và nạp plugin stage.
"""

from typing import Dict, Optional
from .stage import CognitiveStage


class StageRegistry:
    """
    StageRegistry quản lý toàn bộ stage của SciOS-NG.
    """

    def __init__(self) -> None:
        self._stages: Dict[str, CognitiveStage] = {}

    # -----------------------------------------------------
    # Registration
    # -----------------------------------------------------

    def register(self, stage: CognitiveStage) -> None:
        """Đăng ký một stage vào registry."""
        self._stages[stage.name] = stage

    def unregister(self, name: str) -> None:
        """Xoá một stage khỏi registry."""
        if name in self._stages:
            del self._stages[name]

    def get(self, name: str) -> Optional[CognitiveStage]:
        """Lấy stage theo tên."""
        return self._stages.get(name)

    def all(self) -> Dict[str, CognitiveStage]:
        """Trả về toàn bộ stage."""
        return dict(self._stages)

    def clear(self) -> None:
        """Xoá toàn bộ stage."""
        self._stages.clear()

    # -----------------------------------------------------
    # Plugin Loading (placeholder)
    # -----------------------------------------------------

    def load_plugins(self, path: str) -> None:
        """
        Nạp stage từ thư mục plugin.
        (Placeholder — sẽ hiện thực sau)
        """
        pass

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __len__(self) -> int:
        return len(self._stages)

    def __contains__(self, name: str) -> bool:
        return name in self._stages

    def __repr__(self) -> str:
        return f"<StageRegistry count={len(self._stages)}>"
