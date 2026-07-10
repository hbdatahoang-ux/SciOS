"""
SciOS Kernel State
==================

Quản lý trạng thái tổng thể của CognitiveKernel.
"""

from enum import Enum


class KernelStatus(str, Enum):
    """Các trạng thái hợp lệ của Kernel."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"


class KernelState:
    """
    KernelState lưu trữ trạng thái hiện tại và thông điệp liên quan.
    """

    def __init__(self) -> None:
        self.status: KernelStatus = KernelStatus.IDLE
        self.message: str | None = None

    # -----------------------------------------------------
    # State transitions
    # -----------------------------------------------------

    def set_status(self, status: KernelStatus, message: str | None = None) -> None:
        """Cập nhật trạng thái kernel."""
        self.status = status
        self.message = message

    def is_idle(self) -> bool:
        return self.status == KernelStatus.IDLE

    def is_running(self) -> bool:
        return self.status == KernelStatus.RUNNING

    def is_paused(self) -> bool:
        return self.status == KernelStatus.PAUSED

    def is_error(self) -> bool:
        return self.status == KernelStatus.ERROR

    def is_stopped(self) -> bool:
        return self.status == KernelStatus.STOPPED

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "message": self.message,
        }

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<KernelState status={self.status.value} message={self.message}>"
