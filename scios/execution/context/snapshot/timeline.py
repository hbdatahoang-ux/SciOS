from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot


@dataclass
class ExecutionTimeline:
    """
    ExecutionTimeline = Ordered chain of ExecutionSnapshots.
    Provides history, rollback, branching, and replay.
    """

    snapshots: List[ExecutionSnapshot] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def latest(self) -> Optional[ExecutionSnapshot]:
        """
        Get the most recent snapshot.
        """
        return self.snapshots[-1] if self.snapshots else None

    def add_snapshot(self, snapshot: ExecutionSnapshot) -> None:
        """
        Append new snapshot to timeline.
        """
        self.snapshots.append(snapshot)

    def get_snapshot(self, snapshot_id: UUID) -> Optional[ExecutionSnapshot]:
        """
        Lookup snapshot by ID.
        """
        for s in self.snapshots:
            if s.snapshot_id == snapshot_id:
                return s
        return None

    # =========================================================
    # Rollback / Branching
    # =========================================================

    def rollback(self, steps: int = 1) -> Optional[ExecutionSnapshot]:
        """
        Rollback N steps in timeline.
        """
        if steps <= 0 or steps > len(self.snapshots):
            return None
        target_index = len(self.snapshots) - steps
        return self.snapshots[target_index]

    def branch(self, snapshot_id: UUID) -> "ExecutionTimeline":
        """
        Create new branch starting from given snapshot.
        """
        branch_snapshots = []
        for s in self.snapshots:
            branch_snapshots.append(s)
            if s.snapshot_id == snapshot_id:
                break
        return ExecutionTimeline(snapshots=branch_snapshots)

    # =========================================================
    # Replay
    # =========================================================

    def replay(self) -> List[ExecutionSnapshot]:
        """
        Replay all snapshots sequentially.
        """
        return list(self.snapshots)

    # =========================================================
    # Diff / History
    # =========================================================

    def history(self) -> List[UUID]:
        """
        Return list of snapshot IDs in timeline.
        """
        return [s.snapshot_id for s in self.snapshots]
