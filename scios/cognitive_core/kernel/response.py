"""
SciOS Cognitive Response
========================

CognitiveResponse là output chuẩn của CognitiveKernel.
Nó chứa trạng thái, context cuối cùng, cùng với errors/warnings/metadata.
"""

from dataclasses import dataclass, field
from typing import Any
from .context import CognitiveContext


@dataclass(slots=True)
class CognitiveResponse:
    """
    CognitiveResponse đại diện cho kết quả cuối cùng của pipeline.
    """

    status: str
    context: CognitiveContext
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # -----------------------------------------------------
    # Factory
    # -----------------------------------------------------

    @classmethod
    def from_context(cls, context: CognitiveContext, status: str = "success") -> "CognitiveResponse":
        """Tạo response từ context cuối cùng."""
        return cls(status=status, context=context)

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "context": self.context.to_dict(),
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<CognitiveResponse status={self.status} errors={len(self.errors)}>"
