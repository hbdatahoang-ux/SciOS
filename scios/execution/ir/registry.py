from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from scios.execution.ir.opcode import Opcode
from scios.execution.ir.descriptor import InstructionDescriptor


@dataclass
class InstructionRegistry:
    """
    InstructionRegistry = Central registry for Opcode descriptors.
    """

    descriptors: Dict[Opcode, InstructionDescriptor] = field(default_factory=dict)

    # =========================================================
    # Registration
    # =========================================================

    def register(self, descriptor: InstructionDescriptor) -> None:
        """
        Register a new InstructionDescriptor for an opcode.
        """
        self.descriptors[descriptor.opcode] = descriptor

    def unregister(self, opcode: Opcode) -> None:
        """
        Remove descriptor for an opcode.
        """
        if opcode in self.descriptors:
            del self.descriptors[opcode]

    # =========================================================
    # Lookup
    # =========================================================

    def get(self, opcode: Opcode) -> Optional[InstructionDescriptor]:
        """
        Retrieve descriptor for an opcode.
        """
        return self.descriptors.get(opcode)

    def execute(self, opcode: Opcode, *args, **kwargs):
        """
        Execute handler bound to an opcode.
        """
        descriptor = self.get(opcode)
        if not descriptor:
            raise RuntimeError(f"No descriptor registered for opcode {opcode}")
        return descriptor.execute(*args, **kwargs)

    # =========================================================
    # Utility
    # =========================================================

    def list_opcodes(self) -> list[str]:
        """
        Return list of registered opcode values.
        """
        return [op.value for op in self.descriptors.keys()]

    def to_dict(self) -> dict:
        """
        Serialize registry to dict.
        """
        return {
            op.value: desc.to_dict()
            for op, desc in self.descriptors.items()
        }
