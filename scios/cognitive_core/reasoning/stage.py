"""
SciOS Reasoning Stage
=====================

Pipeline stage that orchestrates Planner, Inference, Hypothesis, Verifier.
"""

from __future__ import annotations
from typing import Any, Dict
from .planner import ReasoningPlanner
from .inference import InferenceEngine
from .hypothesis import HypothesisGenerator
from .verifier import ReasoningVerifier
from .state import ReasoningState


class ReasoningStage:
    """
    ReasoningStage = Pipeline stage that runs the full reasoning pipeline.
    """

    def __init__(self) -> None:
        self._planner = ReasoningPlanner()
        self._inference = InferenceEngine()
        self._hypothesis = HypothesisGenerator()
        self._verifier = ReasoningVerifier()
        self._state = ReasoningState()

    def run(self, query: str, context: dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Execute the reasoning pipeline.
        """
        context = context or {}
        self._state.record(query, context)

        plan = self._planner.create_plan(query, context)
        inference = self._inference.infer(query, context)
        hypothesis = self._hypothesis.generate(query, inference)
        verification = self._verifier.verify(hypothesis, context)

        result = {
            "stage": "ReasoningStage",
            "query": query,
            "plan": plan,
            "inference": inference,
            "hypothesis": hypothesis,
            "verification": verification,
        }
        self._state.record_result(result)
        return result

    def status(self) -> Dict[str, Any]:
        """
        Return reasoning stage status.
        """
        return {
            "stage": "ReasoningStage",
            "records": self._state.status()["records"],
        }

    def reset(self) -> None:
        """
        Reset reasoning stage state.
        """
        self._planner.reset()
        self._inference.reset()
        self._hypothesis.reset()
        self._verifier.reset()
        self._state.reset()
