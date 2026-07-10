from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from uuid import UUID, uuid4

from scios.execution.ir.descriptor import InstructionDescriptor


@dataclass
class InstructionPointer:
    """
    InstructionPointer = Tracks current position in instruction stream.
    """

    pointer_id: UUID = field(default_factory=uuid4)
    index: int = 0
    stream: List[Tuple[InstructionDescriptor, Dict[str, Any]]] = field(default_factory=list)

    # =========================================================
    # Core API
    # =========================================================

    def load_stream(self, instructions: List[Tuple[InstructionDescriptor, Dict[str, Any]]]) -> None:
        """
        Load a new instruction stream.
        """
        self.stream = instructions
        self.index = 0

    def current(self) -> Tuple[InstructionDescriptor, Dict[str, Any]] | None:
        """
        Return current instruction.
        """
        if 0 <= self.index < len(self.stream):
            return self.stream[self.index]
        return None

    def advance(self) -> Tuple[InstructionDescriptor, Dict[str, Any]] | None:
        """
        Move pointer to next instruction and return it.
        """
        self.index += 1
        return self.current()

    def rewind(self) -> Tuple[InstructionDescriptor, Dict[str, Any]] | None:
        """
        Move pointer back one step.
        """
        self.index = max(0, self.index - 1)
        return self.current()

    def reset(self) -> None:
        """
        Reset pointer to beginning.
        """
        self.index = 0

    # =========================================================
    # Utility
    # =========================================================

    def has_next(self) -> bool:
        """
        Check if there are more instructions ahead.
        """
        return self.index + 1 < len(self.stream)

    def position(self) -> int:
        """
        Return current index position.
        """
        return self.index
