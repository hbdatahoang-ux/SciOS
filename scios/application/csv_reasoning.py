from __future__ import annotations

from typing import Any

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.step import ReasoningStep
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.strategies.base import BaseReasoningStrategy


__all__ = [
    "EvidenceDeductiveStrategy",
]


class EvidenceDeductiveStrategy(BaseReasoningStrategy):
    """
    Deductive strategy for interpreting deterministic statistical evidence.

    The strategy consumes evidence already produced by an upstream tool.
    It does not read the source dataset or recompute statistics.
    """

    @property
    def reasoning_type(self) -> ReasoningType:
        return ReasoningType.DEDUCTIVE

    def execute(
        self,
        problem: ReasoningProblem,
    ) -> ReasoningResult:
        if not isinstance(problem, ReasoningProblem):
            raise TypeError("problem must be a ReasoningProblem")

        evidence = problem.context.get("evidence")

        if not isinstance(evidence, dict):
            raise ValueError("ReasoningProblem context must contain evidence")

        required = {
            "column",
            "index",
            "value",
            "q1",
            "q3",
            "iqr",
            "lower_bound",
            "upper_bound",
            "rule",
        }

        missing = required.difference(evidence)

        if missing:
            raise ValueError(
                "evidence is missing required fields: "
                + ", ".join(sorted(missing))
            )

        value = float(evidence["value"])
        lower_bound = float(evidence["lower_bound"])
        upper_bound = float(evidence["upper_bound"])

        is_outlier = (
            value < lower_bound
            or value > upper_bound
        )

        evidence_step = ReasoningStep(
            description="Evaluate statistical evidence using the IQR rule.",
            reasoning_type=self.reasoning_type,
            input=evidence,
            output={
                "value": value,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "is_outlier": is_outlier,
            },
            metadata={
                "evidence_source": "deterministic statistical tool",
                "rule": evidence["rule"],
            },
        )

        conclusion: dict[str, Any] = {
            "column": evidence["column"],
            "index": evidence["index"],
            "value": value,
            "is_outlier": is_outlier,
            "evidence": {
                "rule": evidence["rule"],
                "q1": evidence["q1"],
                "q3": evidence["q3"],
                "iqr": evidence["iqr"],
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "value": value,
            },
        }

        confidence = 1.0 if is_outlier else 0.0

        return ReasoningResult(
            problem=problem,
            steps=[evidence_step],
            conclusion=conclusion,
            accepted=is_outlier,
            metadata={
                "confidence": confidence,
                "confidence_basis": "deterministic IQR evidence",
            },
        )