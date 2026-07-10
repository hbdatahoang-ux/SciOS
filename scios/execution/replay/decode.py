from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any
from uuid import UUID, uuid4

from scios.execution.ir.opcode import Opcode
from scios.execution.ir.descriptor import InstructionDescriptor
from scios.execution.ir.registry import InstructionRegistry


@dataclass
class DecodeUnit:
    """
    DecodeUnit = Responsible for decoding fetched instructions.
    """

    unit_id: UUID = field(default_factory=uuid4)
    registry: InstructionRegistry = field(default_factory=InstructionRegistry)

    # =========================================================
    # Core API
    # =========================================================

    def decode(
        self,
        fetched: Tuple[InstructionDescriptor, Dict[str, Any]],
    ) -> InstructionDescriptor:
        """
        Decode fetched instruction into a descriptor.
        """
        descriptor, payload = fetched
        if not isinstance(descriptor, InstructionDescriptor):
            raise ValueError("Invalid instruction descriptor during decode")
        return descriptor

    def lookup(self, opcode: Opcode) -> InstructionDescriptor | None:
        """
        Lookup descriptor by opcode.
        """
        return self.registry.get(opcode)

    # =========================================================
    # Utility
    # =========================================================

    def register_descriptor(self, descriptor: InstructionDescriptor) -> None:
        """
        Register descriptor in decode unit registry.
        """
        self.registry.register(descriptor)

    def available_opcodes(self) -> list[str]:
        """
        List all opcodes known to decode unit.
        """
        return self.registry.list_opcodes()
