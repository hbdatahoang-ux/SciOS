from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from uuid import UUID, uuid4
from datetime import datetime
from scios.execution.ir.registry import InstructionRegistry
from scios.execution.ir.opcode import Opcode


@dataclass
class IRManifest:
    """
    IRManifest = Snapshot of all registered opcodes and descriptors.
    """

    manifest_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    registry: InstructionRegistry = field(default_factory=InstructionRegistry)

    # =========================================================
    # Core API
    # =========================================================

    def export(self) -> Dict[str, dict]:
        """
        Export manifest as dict of opcode → descriptor metadata.
        """
        return {
            "manifest_id": str(self.manifest_id),
            "timestamp": self.timestamp.isoformat(),
            "opcodes": self.registry.to_dict(),
        }

    def list_opcodes(self) -> list[str]:
        """
        List all opcode values in manifest.
        """
        return self.registry.list_opcodes()

    def has_opcode(self, opcode: Opcode) -> bool:
        """
        Check if opcode exists in manifest.
        """
        return opcode in self.registry.descriptors
