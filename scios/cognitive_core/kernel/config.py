"""
SciOS Kernel Configuration
==========================

Định nghĩa cấu hình chuẩn cho CognitiveKernel.
Bao gồm tham số hệ thống, logging, timeout, và giới hạn pipeline.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class KernelConfig:
    """
    KernelConfig lưu trữ các tham số cấu hình cho CognitiveKernel.
    """

    # -----------------------------------------------------
    # Pipeline
    # -----------------------------------------------------
    max_stages: int = 32
    stage_timeout: int = 30  # giây

    # -----------------------------------------------------
    # Logging
    # -----------------------------------------------------
    log_level: str = "INFO"
    enable_trace: bool = True

    # -----------------------------------------------------
    # Error handling
    # -----------------------------------------------------
    retry_on_error: bool = True
    max_retries: int = 3

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------
    metadata: dict[str, Any] = field(default_factory=dict)

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_stages": self.max_stages,
            "stage_timeout": self.stage_timeout,
            "log_level": self.log_level,
            "enable_trace": self.enable_trace,
            "retry_on_error": self.retry_on_error,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
        }

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<KernelConfig stages={self.max_stages} timeout={self.stage_timeout}s log={self.log_level}>"
