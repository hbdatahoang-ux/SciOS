from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID, uuid4
from scios.execution.node.kind import NodeKind
from scios.execution.node.status import NodeStatus
from scios.execution.node.lifecycle import is_terminal, is_active, is_pending, can_retry


@dataclass
class ExecutionNode:
    """
    ExecutionNode = Atomic unit of execution in IR.
    """

    node_id: UUID = field(default_factory=uuid4)
    kind: NodeKind = NodeKind.PRIMITIVE
    status: NodeStatus = NodeStatus.READY
    name: str = "unnamed"
    metadata: dict[str, Any] = field(default_factory=dict)

    parent: Optional["ExecutionNode"] = None
    children: list["ExecutionNode"] = field(default_factory=list)

    # =========================================================
    # Lifecycle API
    # =========================================================

    def mark_running(self) -> None:
        self.status = NodeStatus.RUNNING

    def mark_success(self) -> None:
        self.status = NodeStatus.SUCCESS

    def mark_failed(self) -> None:
        self.status = NodeStatus.FAILED

    def mark_skipped(self) -> None:
        self.status = NodeStatus.SKIPPED

    def mark_cancelled(self) -> None:
        self.status = NodeStatus.CANCELLED

    def retry(self) -> None:
        if can_retry(self.status):
            self.status = NodeStatus.RETRYING

    # =========================================================
    # Hierarchy API
    # =========================================================

    def add_child(self, child: "ExecutionNode") -> None:
        child.parent = self
        self.children.append(child)

    def is_root(self) -> bool:
        return self.parent is None

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    # =========================================================
    # Status checks
    # =========================================================

    def is_terminal(self) -> bool:
        return is_terminal(self.status)

    def is_active(self) -> bool:
        return is_active(self.status)

    def is_pending(self) -> bool:
        return is_pending(self.status)

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "kind": self.kind.value,
            "status": self.status.value,
            "name": self.name,
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children],
        }
