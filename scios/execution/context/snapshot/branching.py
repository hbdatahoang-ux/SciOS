from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from scios.execution.context.snapshot.snapshot import ExecutionSnapshot


@dataclass
class SnapshotBranchManager:
    """
    SnapshotBranchManager = Provides branching capability for snapshots.
    Allows creating independent branches from a given snapshot.
    """

    branches: dict[UUID, List[ExecutionSnapshot]] = field(default_factory=dict)

    # =========================================================
    # Core API
    # =========================================================

    def create_branch(self, base_snapshot: ExecutionSnapshot) -> UUID:
        """
        Create new branch starting from base snapshot.
        Returns branch ID.
        """
        branch_id = base_snapshot.snapshot_id
        self.branches[branch_id] = [base_snapshot]
        return branch_id

    def add_snapshot(self, branch_id: UUID, snapshot: ExecutionSnapshot) -> bool:
        """
        Add snapshot to a branch.
        """
        if branch_id not in self.branches:
            return False
        self.branches[branch_id].append(snapshot)
        return True

    def get_branch(self, branch_id: UUID) -> Optional[List[ExecutionSnapshot]]:
        """
        Retrieve snapshots in a branch.
        """
        return self.branches.get(branch_id)

    def latest(self, branch_id: UUID) -> Optional[ExecutionSnapshot]:
        """
        Get latest snapshot in branch.
        """
        branch = self.branches.get(branch_id)
        if branch:
            return branch[-1]
        return None

    # =========================================================
    # Utility
    # =========================================================

    def all_branches(self) -> dict[UUID, List[ExecutionSnapshot]]:
        """
        Return all branches with their snapshots.
        """
        return self.branches

    def branch_ids(self) -> List[UUID]:
        """
        Return list of branch IDs.
        """
        return list(self.branches.keys())
