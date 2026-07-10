from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class GraphHistoryEvent:
    """
    GraphHistoryEvent = Atomic change applied to ExecutionGraph.
    """

    event_id: UUID = field(default_factory=uuid4)
    graph_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    action: str = "unknown"   # e.g. "add_node", "remove_edge", "update_metadata"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphHistory:
    """
    GraphHistory = Ordered log of changes applied to ExecutionGraph.
    """

    events: List[GraphHistoryEvent] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def log(self, graph_id: UUID, action: str, details: Dict[str, Any]) -> GraphHistoryEvent:
        """
        Log a new history event.
        """
        event = GraphHistoryEvent(graph_id=graph_id, action=action, details=details)
        self.events.append(event)
        return event

    def latest(self) -> GraphHistoryEvent | None:
        """
        Get latest history event.
        """
        return self.events[-1] if self.events else None

    def filter_by_action(self, action: str) -> List[GraphHistoryEvent]:
        """
        Get all events of a given action type.
        """
        return [e for e in self.events if e.action == action]

    def filter_by_graph(self, graph_id: UUID) -> List[GraphHistoryEvent]:
        """
        Get all events for a specific graph.
        """
        return [e for e in self.events if e.graph_id == graph_id]

    # =========================================================
    # Utility
    # =========================================================

    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Serialize history to list of dicts.
        """
        return [
            {
                "event_id": str(e.event_id),
                "graph_id": str(e.graph_id),
                "timestamp": e.timestamp.isoformat(),
                "action": e.action,
                "details": e.details,
            }
            for e in self.events
        ]
