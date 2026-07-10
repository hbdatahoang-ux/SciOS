from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from scios.execution.context.context import ExecutionContext


@dataclass(frozen=True)
class ExecutionSnapshot:
    """
    ExecutionSnapshot = Immutable checkpoint of ExecutionContext.
    """

    snapshot_id: UUID = field(default_factory=uuid4)
    parent_snapshot_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    context: ExecutionContext = field(default_factory=ExecutionContext)
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================
    # Copy-on-Write mutation API
    # =========================================================

    def fork(self, new_context: Optional[ExecutionContext] = None,
             **overrides) -> "ExecutionSnapshot":
        """
        Create new snapshot from current one.
        """
        data = self.__dict__.copy()
        if new_context:
            data["context"] = new_context
        data.update(overrides)
        return ExecutionSnapshot(**data)

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": str(self.snapshot_id),
            "parent_snapshot_id": str(self.parent_snapshot_id) if self.parent_snapshot_id else None,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.__dict__,
            "metadata": self.metadata,
        }
