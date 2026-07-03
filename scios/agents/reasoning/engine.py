"""
SciOS Reasoning Engine
======================

Unified reasoning facade for SciOS.

The ReasoningEngine exposes a stable public API for all cognitive
reasoning while delegating execution to interchangeable reasoning
backends.

Responsibilities
----------------
- Manage reasoning lifecycle
- Maintain reasoning state
- Coordinate inference pipeline
- Delegate reasoning to backend
- Return structured reasoning results

Current backend
---------------
- Native SciOS reasoning pipeline

Future backends
---------------
- QTC Runtime
- Symbolic Reasoner
- Neural Reasoner
- Hybrid Reasoner
"""

from __future__ import annotations

from typing import Any

from .state import ReasoningState
from .planner import ReasoningPlanner
from .inference import InferenceEngine
from .hypothesis import HypothesisGenerator
from .verifier import ReasoningVerifier


class ReasoningEngine:
    """
    Unified reasoning engine.

    This class is the public reasoning interface used by
    AgentExecutor, Runtime and Kernel.

    Internal reasoning modules may evolve independently without
    affecting callers.
    """

    def __init__(self) -> None:

        self._state = ReasoningState()

        self._planner = ReasoningPlanner()

        self._inference = InferenceEngine()

        self._hypothesis = HypothesisGenerator()

        self._verifier = ReasoningVerifier()

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        """Initialize reasoning subsystem."""

        self._state.reset()

    def shutdown(self) -> None:
        """Shutdown reasoning subsystem."""

        self._state.reset()

    def reset(self) -> None:
        """Reset reasoning state."""

        self._state.reset()

    # ==========================================================
    # Reasoning
    # ==========================================================

    def reason(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a complete reasoning pipeline.
        """

        context = context or {}

        self._state.record(
            query=query,
            context=context,
        )

        plan = self._planner.create_plan(
            query=query,
            context=context,
        )

        inference = self._inference.infer(
            query=query,
            context=context,
        )

        hypothesis = self._hypothesis.generate(
            query=query,
            inference=inference,
        )

        verification = self._verifier.verify(
            hypothesis=hypothesis,
            context=context,
        )

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

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """Return subsystem status."""

        return {
            "component": "ReasoningEngine",
            "planner": self._planner.__class__.__name__,
            "inference": self._inference.__class__.__name__,
            "hypothesis": self._hypothesis.__class__.__name__,
            "verifier": self._verifier.__class__.__name__,
            "state": self._state.status(),
        }

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def state(self) -> ReasoningState:
        """Return reasoning state."""

        return self._state
    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def infer(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Backward-compatible alias.

        Older kernel modules call
        ReasoningEngine.infer().

        The canonical public API is reason().
        """

        return self.reason(
            query=query,
            context=context,
        )        