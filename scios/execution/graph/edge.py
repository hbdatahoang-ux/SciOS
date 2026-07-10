from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class ExecutionEdge:
    """
    ExecutionEdge = Directed edge between two ExecutionNodes.
    Represents dependency or data flow in ExecutionGraph.
    """

    edge_id: UUID = field(default_factory=uuid4)
    source_id: UUID = field(default_factory=uuid4)
    target_id: UUID = field(default_factory=uuid4)

    # Optional metadata: type of dependency, conditions, labels
    label: str = "dependency"
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================
    # Utility
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": str(self.edge_id),
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "label": self.label,
            "metadata": self.metadata,
        }

    def is_self_loop(self) -> bool:
        """
        Check if edge is a self-loop (source == target).
        """
        return self.source_id == self.target_id
