from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import UUID, uuid4

from scios.cognitive_core.reasoning.rules import RuleBase
from scios.cognitive_core.reasoning.reasoning import ReasoningEngine


@dataclass
class ProblemSolver:
    """
    ProblemSolver = Applies rules + reasoning to solve problems.
    """

    solver_id: UUID = field(default_factory=uuid4)
    rulebase: RuleBase = field(default_factory=RuleBase)
    engine: ReasoningEngine = field(default_factory=ReasoningEngine)

    # =========================================================
    # Core API
    # =========================================================

    def solve(self, problem: Dict[str, Any]) -> List[str]:
        """
        Solve a problem by applying rules and reasoning.
        """
        solutions = []

        # Step 1: Apply rules
        for rule in self.rulebase.get_rules():
            if rule["condition"] in problem.values():
                solutions.append(f"Rule applied: {rule['condition']} → {rule['conclusion']}")

        # Step 2: Use reasoning engine
        inferred = self.engine.infer(problem)
        solutions.extend([f"Inferred: {c}" for c in inferred])

        # Step 3: Reason about goal if present
        if "goal" in problem:
            goal_conclusions = self.engine.reason_about_goal(problem["goal"])
            solutions.extend(goal_conclusions)

        return solutions

    # =========================================================
    # Utility
    # =========================================================

    def reset(self) -> None:
        """
        Reset solver state.
        """
        self.rulebase.clear()
        self.engine.reset()
