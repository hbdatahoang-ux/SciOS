from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from scios.execution.graph.change.change import GraphChange


@dataclass
class GraphChangeSet:
    """
    GraphChangeSet = Collection of GraphChanges.
    """

    changes: List[GraphChange] = field(default_factory=list)

    def add(self, change: GraphChange) -> None:
        self.changes.append(change)

    def to_dict(self) -> List[dict]:
        return [c.to_dict() for c in self.changes]
