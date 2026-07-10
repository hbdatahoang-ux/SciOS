from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Iterator
from uuid import UUID
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot


@dataclass
class SnapshotReplayEngine:
    """
    SnapshotReplayEngine = Replay snapshot stream sequentially.
    Provides deterministic reconstruction of ExecutionContext history.
    """

    snapshots: List[ExecutionSnapshot] = field(default_factory=list)
    pointer: int = 0

    # =========================================================
    # Core API
    # =========================================================

    def load(self, snapshots: List[ExecutionSnapshot]) -> None:
        """
        Load snapshot stream into engine.
        """
        self.snapshots = snapshots
        self.pointer = 0

    def reset(self) -> None:
        """
        Reset replay pointer.
        """
        self.pointer = 0

    def next(self) -> Optional[ExecutionSnapshot]:
        """
        Advance replay pointer and return next snapshot.
        """
        if self.pointer < len(self.snapshots):
            snapshot = self.snapshots[self.pointer]
            self.pointer += 1
            return snapshot
        return None

    def peek(self) -> Optional[ExecutionSnapshot]:
        """
        Peek current snapshot without advancing.
        """
        if self.pointer < len(self.snapshots):
            return self.snapshots[self.pointer]
        return None

    def replay_all(self) -> Iterator[ExecutionSnapshot]:
        """
        Replay all snapshots sequentially.
        """
        self.reset()
        while True:
            snap = self.next()
            if not snap:
                break
            yield snap

    # =========================================================
    # Utility
    # =========================================================

    def has_more(self) -> bool:
        """
        Check if more snapshots remain.
        """
        return self.pointer < len(self.snapshots)

    def current_index(self) -> int:
        """
        Get current replay pointer index.
        """
        return self.pointer
