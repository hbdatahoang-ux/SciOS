from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from scios.execution.node.node import ExecutionNode


@dataclass
class Worker:
    """
    Worker = Executes a single node.
    """

    worker_id: UUID = field(default_factory=uuid4)
    busy: bool = False

    # =========================================================
    # Core API
    # =========================================================

    def execute(self, node: ExecutionNode) -> Any:
        """
        Execute node and return result.
        """
        self.busy = True
        try:
            # Node handler is expected to be a callable
            handler = node.handler
            result = handler(node.inputs)
            return result
        finally:
            self.busy = False

    # =========================================================
    # Utility
    # =========================================================

    def is_available(self) -> bool:
        """
        Check if worker is free.
        """
        return not self.busy
