from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from uuid import UUID, uuid4

from scios.execution.ir.descriptor import InstructionDescriptor


@dataclass
class FetchUnit:
    """
    FetchUnit = Responsible for fetching instructions from memory/queue.
    """

    unit_id: UUID = field(default_factory=uuid4)
    instruction_queue: List[Tuple[InstructionDescriptor, Dict[str, Any]]] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def load_instructions(self, instructions: List[Tuple[InstructionDescriptor, Dict[str, Any]]]) -> None:
        """
        Load a batch of instructions into the queue.
        """
        self.instruction_queue.extend(instructions)

    def fetch_next(self) -> Tuple[InstructionDescriptor, Dict[str, Any]] | None:
        """
        Fetch the next instruction from the queue.
        """
        if not self.instruction_queue:
            return None
        return self.instruction_queue.pop(0)

    def peek_next(self) -> Tuple[InstructionDescriptor, Dict[str, Any]] | None:
        """
        Peek at the next instruction without removing it.
        """
        return self.instruction_queue[0] if self.instruction_queue else None

    def has_instructions(self) -> bool:
        """
        Check if there are instructions left in the queue.
        """
        return len(self.instruction_queue) > 0

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Clear instruction queue.
        """
        self.instruction_queue.clear()
