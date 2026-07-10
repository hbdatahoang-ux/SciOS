from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from scios.execution.graph.graph import ExecutionGraph


@dataclass
class GraphRevision:
    """
    GraphRevision = Immutable snapshot of ExecutionGraph at a point in time.
    """

    revision_id: UUID = field(default_factory=uuid4)
    graph_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = "revision"
    graph_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRevisionManager:
    """
    GraphRevisionManager = Manages revisions of an ExecutionGraph.
    """

    revisions: List[GraphRevision] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def commit(self, graph: ExecutionGraph, description: str = "") -> GraphRevision:
        """
        Commit current graph state as a new revision.
        """
        revision = GraphRevision(
            graph_id=graph.graph_id,
            description=description or f"Revision at {datetime.utcnow().isoformat()}",
            graph_state=graph.to_dict(),
        )
        self.revisions.append(revision)
        return revision

    def latest(self) -> GraphRevision | None:
        """
        Get latest revision.
        """
        return self.revisions[-1] if self.revisions else None

    def rollback(self, revision_id: UUID) -> Dict[str, Any] | None:
        """
        Rollback to a specific revision by ID.
        Returns graph_state dict.
        """
        for rev in self.revisions:
            if rev.revision_id == revision_id:
                # Trim history to this revision
                idx = self.revisions.index(rev)
                self.revisions = self.revisions[: idx + 1]
                return rev.graph_state
        return None

    # =========================================================
    # Utility
    # =========================================================

    def history(self) -> List[UUID]:
        """
        Return list of revision IDs.
        """
        return [rev.revision_id for rev in self.revisions]

    def describe(self) -> List[str]:
        """
        Return human-readable descriptions of revisions.
        """
        return [f"{rev.revision_id} - {rev.description}" for rev in self.revisions]
