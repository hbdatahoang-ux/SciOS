"""
Replay VM (CPU) Subsystem
=========================

Provides virtual machine pipeline for executing IR instructions:
- ReplayEngine: High-level CPU orchestrator
- FetchUnit: Fetch stage (load instructions)
- DecodeUnit: Decode stage (map opcode → descriptor)
- ExecuteUnit: Execute stage (run handler)
- InstructionPointer: Tracks current position in stream
- Pipeline: Full pipeline (Fetch → Decode → Execute → Commit)
"""

from scios.execution.replay.engine import ReplayEngine
from scios.execution.replay.fetch import FetchUnit
from scios.execution.replay.decode import DecodeUnit
from scios.execution.replay.execute import ExecuteUnit
from scios.execution.replay.pointer import InstructionPointer
from scios.execution.replay.pipeline import Pipeline

__all__ = [
    "ReplayEngine",
    "FetchUnit",
    "DecodeUnit",
    "ExecuteUnit",
    "InstructionPointer",
    "Pipeline",
]
