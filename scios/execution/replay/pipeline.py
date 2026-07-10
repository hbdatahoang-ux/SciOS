from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
from uuid import UUID, uuid4

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.ir.descriptor import InstructionDescriptor
from scios.execution.replay.fetch import FetchUnit
from scios.execution.replay.decode import DecodeUnit
from scios.execution.replay.execute import ExecuteUnit
from scios.execution.replay.pointer import InstructionPointer


@dataclass
class Pipeline:
    """
    Pipeline = CPU pipeline for ReplayEngine.
    Stages: Fetch → Decode → Execute → Commit
    """

    pipeline_id: UUID = field(default_factory=uuid4)
    fetch_unit: FetchUnit = field(default_factory=FetchUnit)
    decode_unit: DecodeUnit = field(default_factory=DecodeUnit)
    execute_unit: ExecuteUnit = field(default_factory=ExecuteUnit)
    pointer: InstructionPointer = field(default_factory=InstructionPointer)

    # =========================================================
    # Core API
    # =========================================================

    def load_instructions(self, instructions: List[Tuple[InstructionDescriptor, Dict[str, Any]]]) -> None:
        """
        Load instruction stream into pipeline.
        """
        self.fetch_unit.load_instructions(instructions)
        self.pointer.load_stream(instructions)

    def step(self, graph: ExecutionGraph) -> Any:
        """
        Execute one pipeline step (Fetch → Decode → Execute).
        """
        fetched = self.fetch_unit.fetch_next()
        if not fetched:
            return None

        decoded = self.decode_unit.decode(fetched)
        result = self.execute_unit.execute(graph, (decoded, fetched[1]))
        self.pointer.advance()
        return result

    def run(self, graph: ExecutionGraph) -> List[Any]:
        """
        Run full pipeline until instructions exhausted.
        """
        results = []
        while self.fetch_unit.has_instructions():
            result = self.step(graph)
            results.append(result)
        return results

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Reset pipeline state.
        """
        self.fetch_unit.reset()
        self.pointer.reset()
