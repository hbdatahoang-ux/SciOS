from __future__ import annotations
from dataclasses import dataclass
from typing import List
from scios.execution.node.node import ExecutionNode


@dataclass
class CostModel:
    """
    CostModel = Predicts and refines execution order based on cost.
    """

    mode: str = "time"  # default cost model

    # =========================================================
    # Core API
    # =========================================================

    def estimate(self, node: ExecutionNode) -> float:
        """
        Estimate cost of a node based on mode.
        """
        if self.mode == "time":
            # Ước lượng chi phí dựa trên thời gian dự kiến
            return node.metadata.get("expected_time", 1.0)
        elif self.mode == "resources":
            # Ước lượng chi phí dựa trên tài nguyên (CPU, memory)
            return node.metadata.get("resource_cost", 1.0)
        elif self.mode == "hybrid":
            # Kết hợp cả thời gian và tài nguyên
            t = node.metadata.get("expected_time", 1.0)
            r = node.metadata.get("resource_cost", 1.0)
            return t + r
        else:
            raise ValueError(f"Unknown cost model mode: {self.mode}")

    def refine(self, nodes: List[ExecutionNode]) -> List[ExecutionNode]:
        """
        Reorder nodes based on estimated cost.
        """
        return sorted(nodes, key=lambda n: self.estimate(n))

    # =========================================================
    # Utility
    # =========================================================

    def set_mode(self, mode: str) -> None:
        """
        Change cost model mode.
        """
        self.mode = mode
