"""
SciOS Kernel Hooks
==================

Định nghĩa hệ thống hook cho CognitiveKernel.
Cho phép gắn hành vi bổ sung trước/after stage hoặc kernel run.
"""

from typing import Callable, List
from .context import CognitiveContext
from .stage import CognitiveStage


class HookManager:
    """
    HookManager quản lý before/after hooks cho stage và kernel.
    """

    def __init__(self) -> None:
        self.before_stage: List[Callable[[CognitiveStage, CognitiveContext], None]] = []
        self.after_stage: List[Callable[[CognitiveStage, CognitiveContext], None]] = []
        self.before_kernel: List[Callable[[CognitiveContext], None]] = []
        self.after_kernel: List[Callable[[CognitiveContext], None]] = []

    # -----------------------------------------------------
    # Registration
    # -----------------------------------------------------

    def register_before_stage(self, fn: Callable[[CognitiveStage, CognitiveContext], None]) -> None:
        self.before_stage.append(fn)

    def register_after_stage(self, fn: Callable[[CognitiveStage, CognitiveContext], None]) -> None:
        self.after_stage.append(fn)

    def register_before_kernel(self, fn: Callable[[CognitiveContext], None]) -> None:
        self.before_kernel.append(fn)

    def register_after_kernel(self, fn: Callable[[CognitiveContext], None]) -> None:
        self.after_kernel.append(fn)

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    def run_before_stage(self, stage: CognitiveStage, context: CognitiveContext) -> None:
        for fn in self.before_stage:
            fn(stage, context)

    def run_after_stage(self, stage: CognitiveStage, context: CognitiveContext) -> None:
        for fn in self.after_stage:
            fn(stage, context)

    def run_before_kernel(self, context: CognitiveContext) -> None:
        for fn in self.before_kernel:
            fn(context)

    def run_after_kernel(self, context: CognitiveContext) -> None:
        for fn in self.after_kernel:
            fn(context)

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<HookManager before_stage={len(self.before_stage)} after_stage={len(self.after_stage)}>"
