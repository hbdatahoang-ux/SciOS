from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Any

from scios.execution.node.kind import NodeKind
from scios.execution.node.status import NodeStatus
from scios.execution.operation.ref import OperationRef


@dataclass
class ExecutionNode:
    """
    Canonical execution IR node.
    """

    node_id: UUID = field(default_factory=uuid4)
    kind: NodeKind = NodeKind.PRIMITIVE
    name: str = "unnamed"
    status: NodeStatus = NodeStatus.READY
    operation_ref: OperationRef | None = None

    source: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": str(self.node_id),
            "kind": self.kind.value,
            "name": self.name,
            "status": self.status.value,
            "operation_ref": (
                {
                    "name": self.operation_ref.name,
                    "version": self.operation_ref.version,
                }
                if self.operation_ref is not None
                else None
            ),
            "source": dict(self.source),
            "metadata": dict(self.metadata),
        }
