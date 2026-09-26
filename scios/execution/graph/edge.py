from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass
class ExecutionEdge:
    """
    Directed relationship between two ExecutionNodes.

    An edge represents a dependency relation in an ExecutionGraph.
    """

    source_id: UUID
    target_id: UUID

    edge_id: UUID = field(default_factory=uuid4)
    relation: str = "dependency"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": str(self.edge_id),
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "relation": self.relation,
            "metadata": dict(self.metadata),
        }

    def is_self_loop(self) -> bool:
        return self.source_id == self.target_id
