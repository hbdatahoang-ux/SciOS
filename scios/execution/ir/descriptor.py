from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, Any
from uuid import UUID, uuid4
from scios.execution.ir.opcode import Opcode


@dataclass
class InstructionDescriptor:
    """
    InstructionDescriptor = Metadata + handler for an Opcode.
    """

    descriptor_id: UUID = field(default_factory=uuid4)
    opcode: Opcode = Opcode.ADD_NODE
    description: str = "instruction"
    handler: Callable[..., Any] | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # =========================================================
    # Execution
    # =========================================================

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the handler bound to this opcode.
        """
        if not self.handler:
            raise RuntimeError(f"No handler bound for opcode {self.opcode}")
        return self.handler(*args, **kwargs)

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "descriptor_id": str(self.descriptor_id),
            "opcode": self.opcode.value,
            "description": self.description,
            "metadata": self.metadata,
        }
