from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import UUID
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot


@dataclass
class SnapshotStore:
    """
    SnapshotStore = Storage layer for ExecutionSnapshots.
    Supports in-memory and extensible persistent backends.
    """

    snapshots: Dict[UUID, ExecutionSnapshot] = field(default_factory=dict)

    # =========================================================
    # Core API
    # =========================================================

    def save(self, snapshot: ExecutionSnapshot) -> None:
        """
        Save snapshot into store.
        """
        self.snapshots[snapshot.snapshot_id] = snapshot

    def load(self, snapshot_id: UUID) -> Optional[ExecutionSnapshot]:
        """
        Load snapshot by ID.
        """
        return self.snapshots.get(snapshot_id)

    def delete(self, snapshot_id: UUID) -> bool:
        """
        Delete snapshot by ID.
        """
        if snapshot_id in self.snapshots:
            del self.snapshots[snapshot_id]
            return True
        return False

    def latest(self) -> Optional[ExecutionSnapshot]:
        """
        Get most recent snapshot (by insertion order).
        """
        if not self.snapshots:
            return None
        # Python 3.7+ dict preserves insertion order
        return list(self.snapshots.values())[-1]

    # =========================================================
    # Utility
    # =========================================================

    def all_snapshots(self) -> list[ExecutionSnapshot]:
        """
        Return all snapshots in store.
        """
        return list(self.snapshots.values())

    def clear(self) -> None:
        """
        Clear all snapshots.
        """
        self.snapshots.clear()
