"""
SciOS Kernel Lifecycle
======================

Quản lý vòng đời của CognitiveKernel:
- Boot (khởi động)
- Shutdown (tắt)
- Restart (khởi động lại)
"""

from .kernel import CognitiveKernel


class KernelLifecycle:
    """
    KernelLifecycle quản lý vòng đời của CognitiveKernel.
    """

    def __init__(self, kernel: CognitiveKernel) -> None:
        self.kernel = kernel
        self.status: str = "idle"

    # -----------------------------------------------------
    # Boot
    # -----------------------------------------------------

    def boot(self) -> None:
        """Khởi động kernel."""
        if self.status != "idle":
            raise RuntimeError("Kernel đã được khởi động hoặc đang chạy")
        self.status = "running"

    # -----------------------------------------------------
    # Shutdown
    # -----------------------------------------------------

    def shutdown(self) -> None:
        """Tắt kernel và giải phóng tài nguyên."""
        if self.status == "idle":
            return
        self.kernel.reset()
        self.status = "stopped"

    # -----------------------------------------------------
    # Restart
    # -----------------------------------------------------

    def restart(self) -> None:
        """Khởi động lại kernel."""
        self.shutdown()
        self.boot()

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<KernelLifecycle status={self.status}>"
