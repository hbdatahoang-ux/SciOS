from __future__ import annotations
from typing import Any, Dict
from scios.execution.ir.opcode import Opcode
from scios.execution.ir.descriptor import InstructionDescriptor


class InstructionValidator:
    """
    InstructionValidator = Validates opcode and payload before execution.
    """

    # =========================================================
    # Opcode validation
    # =========================================================

    def validate_opcode(self, opcode: Opcode) -> None:
        if not isinstance(opcode, Opcode):
            raise ValueError(f"Invalid opcode type: {opcode}")

    # =========================================================
    # Descriptor validation
    # =========================================================

    def validate_descriptor(self, descriptor: InstructionDescriptor) -> None:
        if not descriptor.opcode:
            raise ValueError("Descriptor missing opcode")
        if not descriptor.handler:
            raise ValueError(f"Descriptor for {descriptor.opcode} has no handler")

    # =========================================================
    # Payload validation
    # =========================================================

    def validate_payload(self, opcode: Opcode, payload: Dict[str, Any]) -> None:
        """
        Validate payload structure depending on opcode.
        """
        if opcode in {Opcode.ADD_NODE, Opcode.UPDATE_NODE}:
            if "node_id" not in payload and opcode == Opcode.UPDATE_NODE:
                raise ValueError("Payload missing node_id for update_node")
        elif opcode in {Opcode.ADD_EDGE, Opcode.UPDATE_EDGE}:
            if "source_id" not in payload or "target_id" not in payload:
                raise ValueError("Payload missing source_id/target_id for edge")
        elif opcode in {Opcode.REMOVE_NODE, Opcode.REMOVE_EDGE}:
            if "target_id" not in payload:
                raise ValueError("Payload missing target_id for removal")

    # =========================================================
    # Combined validation
    # =========================================================

    def validate(self, descriptor: InstructionDescriptor, payload: Dict[str, Any]) -> None:
        """
        Validate descriptor + payload together.
        """
        self.validate_descriptor(descriptor)
        self.validate_payload(descriptor.opcode, payload)
