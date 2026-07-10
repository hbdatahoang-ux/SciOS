from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from uuid import UUID, uuid4

from scios.execution.ir.descriptor import InstructionDescriptor
from scios.execution.ir.validator import InstructionValidator
from scios.execution.graph.graph import ExecutionGraph


@dataclass
class ExecuteUnit:
    """
    ExecuteUnit = Responsible for executing decoded instructions.
    """

    unit_id: UUID = field(default_factory=uuid4)
    validator: InstructionValidator = field(default_factory=InstructionValidator)

    # =========================================================
    # Core API
    # =========================================================

    def execute(
        self,
        graph: ExecutionGraph,
        decoded: Tuple[InstructionDescriptor, Dict[str, Any]],
    ) -> Any:
        """
        Execute a decoded instruction on the graph.
        """
        descriptor, payload = decoded

        # Validate before execution
        self.validator.validate(descriptor, payload)

        # Dispatch to handler
        return descriptor.execute(graph, **payload)

    # =========================================================
    # Utility
    # =========================================================

    def safe_execute(
        self,
        graph: ExecutionGraph,
        decoded: Tuple[InstructionDescriptor, Dict[str, Any]],
    ) -> tuple[bool, Any]:
        """
        Execute instruction with error handling.
        Returns (success, result or error).
        """
        try:
            result = self.execute(graph, decoded)
            return True, result
        except Exception as e:
            return False, str(e)
