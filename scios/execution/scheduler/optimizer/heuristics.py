from __future__ import annotations
from dataclasses import dataclass
from typing import List
from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode


@dataclass
class HeuristicStrategy:
    """
    HeuristicStrategy = Defines heuristic-based scheduling strategies.
    """

    mode: str = "min_depth"  # default heuristic

    # =========================================================
    # Core API
    # =========================================================

    def apply(self, graph: ExecutionGraph) -> List[ExecutionNode]:
        """
        Apply heuristic strategy to reorder nodes.
        """
        if self.mode == "min_depth":
            # Ưu tiên node có độ sâu nhỏ nhất trong DAG
            return sorted(graph.nodes.values(), key=lambda n: n.metadata.get("depth", 0))
        elif self.mode == "min_dependencies":
            # Ưu tiên node có ít dependency nhất
            return sorted(graph.nodes.values(), key=lambda n: len(n.dependencies))
        elif self.mode == "balance_load":
            # Ưu tiên node theo trọng số workload (metadata)
            return sorted(graph.nodes.values(), key=lambda n: n.metadata.get("workload", 1))
        else:
            raise ValueError(f"Unknown heuristic mode: {self.mode}")

    # =========================================================
    # Utility
    # =========================================================

    def set_mode(self, mode: str) -> None:
        """
        Change heuristic mode.
        """
        self.mode = mode
