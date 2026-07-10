from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import UUID, uuid4


@dataclass
class GraphChange:
    """
    GraphChange = Atomic change to ExecutionGraph.
    """

    change_id: UUID = field(default_factory=uuid4)
    action: str = "unknown"   # e.g. "add_node", "remove_edge", "update_metadata"
    target_id: UUID | None = None
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_id": str(self.change_id),
            "action": self.action,
            "target_id": str(self.target_id) if self.target_id else None,
            "payload": self.payload,
        }
