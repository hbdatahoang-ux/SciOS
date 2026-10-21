from __future__ import annotations

from typing import Any

import pytest

from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.step import ReasoningStep
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.cognitive_core.reasoning.strategies.base import BaseReasoningStrategy


class TestEvidenceDeductiveStrategyContract:
    """Contract tests for evidence-grounded deductive reasoning."""

    def _make_problem(self) -> ReasoningProblem:
        return ReasoningProblem(
            query="Why is value 100 an anomaly?",
            reasoning_type=ReasoningType.DEDUCTIVE,
            context={
                "evidence": {
                    "column": "value",
                    "index": 5,
                    "value": 100.0,
                    "q1": 10.75,
                    "q3": 13.75,
                    "iqr": 3.0,
                    "lower_bound": 6.25,
                    "upper_bound": 18.25,
                    "rule": "IQR",
                }
            },
        )

    def test_strategy_implements_existing_reasoning_contract(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()

        assert isinstance(strategy, BaseReasoningStrategy)
        assert strategy.reasoning_type is ReasoningType.DEDUCTIVE

    def test_strategy_returns_reasoning_result(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()
        problem = self._make_problem()

        result = strategy.execute(problem)

        assert isinstance(result, ReasoningResult)
        assert result.problem is problem

    def test_reasoning_result_contains_evidence_grounded_steps(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()
        problem = self._make_problem()

        result = strategy.execute(problem)

        assert result.steps
        assert all(
            isinstance(step, ReasoningStep)
            for step in result.steps
        )

        descriptions = [
            step.description.lower()
            for step in result.steps
        ]

        assert any("evidence" in description for description in descriptions)
        assert any("iqr" in description for description in descriptions)

    def test_conclusion_identifies_statistical_outlier(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()
        problem = self._make_problem()

        result = strategy.execute(problem)

        assert result.accepted is True
        assert isinstance(result.conclusion, dict)

        assert result.conclusion["column"] == "value"
        assert result.conclusion["index"] == 5
        assert result.conclusion["value"] == 100.0
        assert result.conclusion["is_outlier"] is True

    def test_conclusion_preserves_supporting_evidence(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()
        problem = self._make_problem()

        result = strategy.execute(problem)

        evidence = result.conclusion["evidence"]

        assert evidence["rule"] == "IQR"
        assert evidence["lower_bound"] == 6.25
        assert evidence["upper_bound"] == 18.25
        assert evidence["value"] == 100.0

    def test_confidence_is_evidence_based(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()
        problem = self._make_problem()

        result = strategy.execute(problem)

        assert "confidence" in result.metadata
        assert 0.0 <= result.metadata["confidence"] <= 1.0

        assert result.metadata["confidence_basis"] == (
            "deterministic IQR evidence"
        )

    def test_reasoner_does_not_claim_causal_explanation(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()
        problem = self._make_problem()

        result = strategy.execute(problem)

        conclusion = result.conclusion

        assert "possible_causes" not in conclusion
        assert "cause" not in conclusion
        assert "causal_explanation" not in conclusion

    def test_invalid_problem_is_rejected(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()

        with pytest.raises(TypeError):
            strategy.execute("not-a-reasoning-problem")

    def test_missing_evidence_is_rejected(self) -> None:
        from scios.application.csv_reasoning import (
            EvidenceDeductiveStrategy,
        )

        strategy = EvidenceDeductiveStrategy()

        problem = ReasoningProblem(
            query="Why is this value anomalous?",
            reasoning_type=ReasoningType.DEDUCTIVE,
            context={},
        )

        with pytest.raises(ValueError, match="evidence"):
            strategy.execute(problem)
