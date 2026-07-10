from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot


@dataclass
class SnapshotRollbackManager:
    """
    SnapshotRollbackManager = Provides rollback capability for snapshots.
    """

    snapshots: List[ExecutionSnapshot] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def add_snapshot(self, snapshot: ExecutionSnapshot) -> None:
        """
        Add snapshot to rollback history.
        """
        self.snapshots.append(snapshot)

    def rollback_to(self, snapshot_id: UUID) -> Optional[ExecutionSnapshot]:
        """
        Rollback to a specific snapshot by ID.
        """
        for i, snap in enumerate(self.snapshots):
            if snap.snapshot_id == snapshot_id:
                # Trim history to this point
                self.snapshots = self.snapshots[: i + 1]
                return snap
        return None

    def rollback_steps(self, steps: int = 1) -> Optional[ExecutionSnapshot]:
        """
        Rollback N steps backwards.
        """
        if steps <= 0 or steps > len(self.snapshots):
            return None
        target_index = len(self.snapshots) - steps
        self.snapshots = self.snapshots[: target_index + 1]
        return self.snapshots[-1]

    def latest(self) -> Optional[ExecutionSnapshot]:
        """
        Get latest snapshot after rollback.
        """
        return self.snapshots[-1] if self.snapshots else None

    # =========================================================
    # Utility
    # =========================================================

    def history(self) -> List[UUID]:
        """
        Return list of snapshot IDs in rollback history.
        """
        return [s.snapshot_id for s in self.snapshots]
