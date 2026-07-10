from __future__ import annotations
from dataclasses import dataclass
from typing import List
from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode


@dataclass
class SchedulingPolicy:
    """
    SchedulingPolicy = Defines strategies for ordering execution of nodes.
    """

    mode: str = "topological"  # default policy

    # =========================================================
    # Core API
    # =========================================================

    def apply(self, graph: ExecutionGraph) -> List[ExecutionNode]:
        """
        Apply scheduling policy to graph and return ordered nodes.
        """
        if self.mode == "fifo":
            return list(graph.nodes.values())
        elif self.mode == "topological":
            return graph.topological_sort()
        elif self.mode == "priority":
            return sorted(graph.nodes.values(), key=lambda n: n.metadata.get("priority", 0), reverse=True)
        else:
            raise ValueError(f"Unknown scheduling policy: {self.mode}")

    # =========================================================
    # Utility
    # =========================================================

    def set_mode(self, mode: str) -> None:
        """
        Change scheduling mode.
        """
        self.mode = mode
