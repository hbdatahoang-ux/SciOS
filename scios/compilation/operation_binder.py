from __future__ import annotations

from typing import Protocol

from scios.cognitive_core.planner.task import Task
from scios.execution.operation.ref import OperationRef


class OperationBinder(Protocol):
    """Explicitly binds a cognitive Task to an executable operation."""

    def bind(self, task: Task) -> OperationRef | None:
        ...
