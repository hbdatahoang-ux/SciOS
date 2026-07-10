from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot


@dataclass
class SnapshotDiff:
    """
    SnapshotDiff = Compute differences between two snapshots.
    """

    before: ExecutionSnapshot
    after: ExecutionSnapshot

    # =========================================================
    # Core API
    # =========================================================

    def diff_context(self) -> Dict[str, Any]:
        """
        Compare ExecutionContext dictionaries between snapshots.
        Returns dict of changes.
        """
        before_ctx = self.before.context.__dict__
        after_ctx = self.after.context.__dict__

        changes = {}
        for key in set(before_ctx.keys()).union(after_ctx.keys()):
            b_val = before_ctx.get(key)
            a_val = after_ctx.get(key)
            if b_val != a_val:
                changes[key] = {"before": b_val, "after": a_val}
        return changes

    def diff_metadata(self) -> Dict[str, Any]:
        """
        Compare metadata between snapshots.
        """
        changes = {}
        for key in set(self.before.metadata.keys()).union(self.after.metadata.keys()):
            b_val = self.before.metadata.get(key)
            a_val = self.after.metadata.get(key)
            if b_val != a_val:
                changes[key] = {"before": b_val, "after": a_val}
        return changes

    def diff_all(self) -> Dict[str, Any]:
        """
        Compute full diff (context + metadata).
        """
        return {
            "context_changes": self.diff_context(),
            "metadata_changes": self.diff_metadata(),
        }
