from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Any

from scios.execution.node.kind import NodeKind
from scios.execution.node.status import NodeStatus


@dataclass
class ExecutionNode:
    """
    Canonical execution IR node.

    An ExecutionNode describes an atomic execution unit.
    It contains semantic and lifecycle information only.

    Runtime execution concerns such as handlers, inputs, workers,
    executors, contexts, and results do not belong here.
    """

    node_id: UUID = field(default_factory=uuid4)
    kind: NodeKind = NodeKind.PRIMITIVE
    name: str = "unnamed"
    status: NodeStatus = NodeStatus.READY

    source: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

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

    # =========================================================
    # Status checks
    # =========================================================

    def is_terminal(self) -> bool:
        return self.status in {
            NodeStatus.SUCCESS,
            NodeStatus.FAILED,
            NodeStatus.SKIPPED,
            NodeStatus.CANCELLED,
        }

    def is_active(self) -> bool:
        return self.status == NodeStatus.RUNNING

    def is_pending(self) -> bool:
        return self.status in {
            NodeStatus.CREATED,
            NodeStatus.READY,
            NodeStatus.WAITING,
        }

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "kind": self.kind.value,
            "name": self.name,
            "status": self.status.value,
            "source": dict(self.source),
            "metadata": dict(self.metadata),
        }
