"""
SciOS Kernel Exceptions
=======================

Định nghĩa các loại lỗi chuẩn trong CognitiveKernel.
Giúp pipeline, dispatcher, stage, lifecycle xử lý lỗi nhất quán.
"""


class KernelError(Exception):
    """Lỗi tổng quát của Kernel."""
    pass


class StageError(KernelError):
    """Lỗi xảy ra trong một stage cụ thể."""

    def __init__(self, stage_name: str, message: str) -> None:
        super().__init__(f"[StageError] Stage '{stage_name}': {message}")
        self.stage_name = stage_name
        self.message = message


class PipelineError(KernelError):
    """Lỗi xảy ra trong pipeline."""

    def __init__(self, message: str) -> None:
        super().__init__(f"[PipelineError] {message}")
        self.message = message


class LifecycleError(KernelError):
    """Lỗi xảy ra trong vòng đời Kernel (boot/shutdown/restart)."""

    def __init__(self, message: str) -> None:
        super().__init__(f"[LifecycleError] {message}")
        self.message = message


class ContextError(KernelError):
    """Lỗi liên quan đến CognitiveContext."""

    def __init__(self, key: str, message: str) -> None:
        super().__init__(f"[ContextError] Key '{key}': {message}")
        self.key = key
        self.message = message
