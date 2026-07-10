"""
SciOS Cognitive Request
=======================

CognitiveRequest là đầu vào chuẩn cho CognitiveKernel.
Nó chứa query, inputs, metadata và thông tin tracing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class CognitiveRequest:
    """
    CognitiveRequest đại diện cho một yêu cầu nhận thức.
    """

    request_id: str
    query: str
    inputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # -----------------------------------------------------
    # Serialization
    # -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "query": self.query,
            "inputs": self.inputs,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    # -----------------------------------------------------
    # Representation
    # -----------------------------------------------------

    def __repr__(self) -> str:
        return f"<CognitiveRequest id={self.request_id} query={self.query}>"
