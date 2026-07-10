from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import UUID, uuid4

from scios.execution.ir.opcode import Opcode
from scios.execution.ir.descriptor import InstructionDescriptor
from scios.execution.ir.registry import InstructionRegistry
from scios.execution.ir.validator import InstructionValidator
from scios.execution.ir.handler import InstructionHandler
from scios.execution.graph.graph import ExecutionGraph


@dataclass
class ReplayEngine:
    """
    ReplayEngine = Virtual Machine (CPU) for executing IR instructions.
    """

    engine_id: UUID = field(default_factory=uuid4)
    registry: InstructionRegistry = field(default_factory=InstructionRegistry)
    validator: InstructionValidator = field(default_factory=InstructionValidator)
    handler: InstructionHandler = field(default_factory=InstructionHandler)

    # =========================================================
    # Instruction Execution
    # =========================================================

    def execute_instruction(
        self,
        graph: ExecutionGraph,
        descriptor: InstructionDescriptor,
        payload: Dict[str, Any],
    ) -> Any:
        """
        Execute a single instruction on the graph.
        """
        # Validate
        self.validator.validate(descriptor, payload)

        # Dispatch
        return descriptor.execute(graph, **payload)

    def execute_sequence(
        self,
        graph: ExecutionGraph,
        instructions: List[tuple[InstructionDescriptor, Dict[str, Any]]],
    ) -> List[Any]:
        """
        Execute a sequence of instructions.
        """
        results = []
        for descriptor, payload in instructions:
            result = self.execute_instruction(graph, descriptor, payload)
            results.append(result)
        return results

    # =========================================================
    # Utility
    # =========================================================

    def load_descriptor(self, opcode: Opcode, description: str, handler_fn) -> None:
        """
        Register a new descriptor with handler.
        """
        descriptor = InstructionDescriptor(
            opcode=opcode,
            description=description,
            handler=handler_fn,
        )
        self.registry.register(descriptor)

    def available_opcodes(self) -> list[str]:
        """
        List all opcodes currently registered in engine.
        """
        return self.registry.list_opcodes()
