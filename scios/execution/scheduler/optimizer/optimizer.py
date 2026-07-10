from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.scheduler.optimizer.heuristics import HeuristicStrategy
from scios.execution.scheduler.optimizer.cost_model import CostModel


@dataclass
class Optimizer:
    """
    Optimizer = Improves execution plan for scheduler.
    """

    optimizer_id: UUID = field(default_factory=uuid4)
    heuristic: HeuristicStrategy = field(default_factory=HeuristicStrategy)
    cost_model: CostModel = field(default_factory=CostModel)

    # =========================================================
    # Core API
    # =========================================================

    def optimize(self, graph: ExecutionGraph) -> List[ExecutionNode]:
        """
        Optimize execution order of nodes in graph.
        """
        # Step 1: Apply heuristic (e.g., minimize depth, balance dependencies)
        ordered_nodes = self.heuristic.apply(graph)

        # Step 2: Evaluate cost model to refine ordering
        optimized_nodes = self.cost_model.refine(ordered_nodes)

        return optimized_nodes

    # =========================================================
    # Utility
    # =========================================================

    def set_heuristic(self, heuristic: HeuristicStrategy) -> None:
        """
        Change heuristic strategy.
        """
        self.heuristic = heuristic

    def set_cost_model(self, cost_model: CostModel) -> None:
        """
        Change cost model.
        """
        self.cost_model = cost_model
