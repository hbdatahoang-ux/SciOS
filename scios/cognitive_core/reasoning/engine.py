"""
SciOS Reasoning Engine
======================

Unified reasoning facade for SciOS.
"""

from __future__ import annotations
from typing import Any, Dict, List

from .state import ReasoningState
from .planner import ReasoningPlanner
from .inference import InferenceEngine
from .hypothesis import HypothesisGenerator
from .verifier import ReasoningVerifier


class ReasoningEngine:
    """
    Unified reasoning engine.
    Provides a stable public API for reasoning pipeline,
    while also supporting rule-based inference and goal reasoning.
    """

    def __init__(self) -> None:
        self._state = ReasoningState()
        self._planner = ReasoningPlanner()
        self._inference = InferenceEngine()
        self._hypothesis = HypothesisGenerator()
        self._verifier = ReasoningVerifier()
        self.rules: List[Dict[str, Any]] = []
        self._running = True

    # ==========================================================
    # Rule management
    # ==========================================================
    def add_rule(self, condition: str, conclusion: str) -> None:
        self.rules.append({"condition": condition, "conclusion": conclusion})

    def clear_rules(self) -> None:
        self.rules.clear()

    # ==========================================================
    # Reasoning pipeline
    # ==========================================================
    def reason(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        self._state.record(query=query, context=context)

        plan = self._planner.create_plan(query=query, context=context)
        inference = self._inference.infer(query=query, context=context)

        # Apply rules
        for rule in self.rules:
            if rule["condition"] in context.values():
                inference.append(f"Rule applied: {rule['condition']} → {rule['conclusion']}")

        hypothesis = self._hypothesis.generate(query=query, inference=inference)
        verification = self._verifier.verify(hypothesis=hypothesis, context=context)

        result = {
            "query": query,
            "plan": plan,
            "inference": inference,
            "hypothesis": hypothesis,
            "verification": verification,
            "accepted": verification.get("accepted", True),
        }

        self._state.record_result(result)
        return result

    def infer(self, context: dict[str, Any]) -> List[str]:
        conclusions = []
        for rule in self.rules:
            if rule["condition"] in context.values():
                conclusions.append(rule["conclusion"])
        if not conclusions:
            conclusions.append(f"Default inference for {context.get('condition', 'unknown')}")
        return conclusions

    def reason_about_goal(self, goal: dict[str, Any]) -> List[str]:
        """
        Simplified goal reasoning using semantic/episodic memory placeholders.
        """
        conclusions = []
        if "event" in goal:
            conclusions.append(f"Goal reasoning: {goal['event']}")
        if "requirements" in goal and goal["requirements"]:
            conclusions.append(f"Requirements: {', '.join(goal['requirements'])}")
        return conclusions

    # ==========================================================
    # Lifecycle
    # ==========================================================
    def reset(self) -> None:
        self._state.reset()
        self.rules.clear()

    # ==========================================================
    # Status
    # ==========================================================
    def status(self) -> dict[str, Any]:
        return {
            "component": "ReasoningEngine",
            "running": self._running,
            "rules_count": len(self.rules),
            "state": self._state.status(),
        }

    @property
    def state(self) -> ReasoningState:
        return self._state
