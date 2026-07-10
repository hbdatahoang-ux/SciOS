"""
SciOS Middleware Manager
========================

Quản lý hook và cross-cutting concerns trong CognitivePipeline.
Được gọi trước và sau mỗi stage để xử lý logging, tracing, metrics, security...
"""

from typing import List, Callable, Any
from .context import CognitiveContext
from .stage import CognitiveStage


class MiddlewareManager:
    """
    MiddlewareManager quản lý danh sách middleware.
    Mỗi middleware là một callable nhận (stage, context).
    """

    def __init__(self) -> None:
        self._before: List[Callable[[CognitiveStage, CognitiveContext], Any]] = []
        self._after: List[Callable[[CognitiveStage, CognitiveContext], Any]] = []

    # -----------------------------------------------------
    # Registration
    # -----------------------------------------------------

    def add_before(self, fn: Callable[[CognitiveStage, CognitiveContext], Any]) -> None:
        """Đăng ký middleware chạy trước stage."""
        self._before.append(fn)

    def add_after(self, fn: Callable[[CognitiveStage, CognitiveContext], Any]) -> None:
        """Đăng ký middleware chạy sau stage."""
        self._after.append(fn)

    def clear(self) -> None:
        """Xoá toàn bộ middleware."""
        self._before.clear()
        self._after.clear()

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    def run_before_stage(self, stage: CognitiveStage, context: CognitiveContext) -> None:
        for fn in self._before:
            fn(stage, context)

    def run_after_stage(self, stage: CognitiveStage, context: CognitiveContext) -> None:
        for fn in self._after:
            fn(stage, context)

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __len__(self) -> int:
        return len(self._before) + len(self._after)

    def __repr__(self) -> str:
        return f"<MiddlewareManager before={len(self._before)} after={len(self._after)}>"
