"""
Intermediate Representation (IR) Subsystem
==========================================

Provides Instruction Set Architecture (ISA) for ExecutionGraph:
- Opcode: Standardized instruction codes
- InstructionDescriptor: Metadata + handler binding
- InstructionRegistry: Central registry for descriptors
- IRManifest: Snapshot of registered opcodes
- InstructionHandler: Concrete implementations of opcodes
- InstructionValidator: Validation layer for descriptors + payloads
"""

from scios.execution.ir.opcode import Opcode
from scios.execution.ir.descriptor import InstructionDescriptor
from scios.execution.ir.registry import InstructionRegistry
from scios.execution.ir.manifest import IRManifest
from scios.execution.ir.handler import InstructionHandler
from scios.execution.ir.validator import InstructionValidator

__all__ = [
    "Opcode",
    "InstructionDescriptor",
    "InstructionRegistry",
    "IRManifest",
    "InstructionHandler",
    "InstructionValidator",
]
