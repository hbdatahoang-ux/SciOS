"""
SciOS Cognitive Response
========================

CognitiveResponse là output chuẩn của CognitiveKernel.

Response chứa:
- trạng thái thực thi
- CognitiveContext cuối cùng
- errors
- warnings
- metadata

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import CognitiveContext


__all__ = [
    "CognitiveResponse",
]


@dataclass(slots=True)
class CognitiveResponse:
    """
    Kết quả cuối cùng của CognitiveKernel pipeline.

    Parameters
    ----------
    status:
        Trạng thái kết quả, ví dụ ``"success"`` hoặc ``"failed"``.

    context:
        CognitiveContext cuối cùng của pipeline.

    errors:
        Danh sách lỗi trong quá trình thực thi.

    warnings:
        Danh sách cảnh báo.

    metadata:
        Metadata bổ sung của response.
    """

    # ======================================================
    # Core
    # ======================================================

    status: str
    context: CognitiveContext

    # ======================================================
    # Diagnostics
    # ======================================================

    errors: list[str] = field(
        default_factory=list,
    )

    warnings: list[str] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # ======================================================
    # Factory
    # ======================================================

    @classmethod
    def from_context(
        cls,
        context: CognitiveContext,
        status: str = "success",
    ) -> "CognitiveResponse":
        """
        Tạo CognitiveResponse từ context cuối cùng.

        Parameters
        ----------
        context:
            CognitiveContext sau khi pipeline hoàn tất.

        status:
            Trạng thái response.
            Mặc định là ``"success"``.
        """

        return cls(
            status=status,
            context=context,
        )

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Chuyển response thành dictionary.

        Context được serialize thông qua ``context.to_dict()``.
        """

        return {
            "status": self.status,
            "context": self.context.to_dict(),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            "<CognitiveResponse "
            f"status={self.status!r} "
            f"errors={len(self.errors)}>"
        )