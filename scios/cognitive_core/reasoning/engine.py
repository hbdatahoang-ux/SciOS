"""
SciOS Reasoning Engine
======================

Unified reasoning facade for the SciOS Cognitive Core.

The :class:`ReasoningEngine` provides a stable, high-level interface
over the complete reasoning pipeline while remaining independent of any
particular reasoning strategy.

Pipeline
--------
Query
    ↓
Planning
    ↓
Inference
    ↓
Hypothesis Generation
    ↓
Verification
    ↓
Reasoning Result

Design Goals
------------
- Stable public API
- Backward compatible
- Stateless public facade
- Strong typing
- Explicit lifecycle
- Runtime independent
- Easily extensible

Python
------
Python 3.11+
"""

from __future__ import annotations

from copy import copy, deepcopy
from typing import Any, Final, TypeAlias

from .hypothesis import HypothesisGenerator
from .inference import InferenceEngine
from .planner import ReasoningPlanner
from .state import ReasoningState
from .verifier import ReasoningVerifier

__all__ = [
    "ReasoningContext",
    "ReasoningRule",
    "ReasoningResult",
    "ReasoningEngine",
]


# ==========================================================
# Type Aliases
# ==========================================================

ReasoningContext: TypeAlias = dict[str, Any]

ReasoningRule: TypeAlias = dict[str, Any]

ReasoningResult: TypeAlias = dict[str, Any]


# ==========================================================
# Constants
# ==========================================================

DEFAULT_COMPONENT_NAME: Final[str] = "ReasoningEngine"

DEFAULT_REASON_QUERY: Final[str] = "reason"

DEFAULT_GOAL_KEY: Final[str] = "goal"

DEFAULT_QUERY_KEY: Final[str] = "query"


# ==========================================================
# Reasoning Engine
# ==========================================================


class ReasoningEngine:
    """
    Unified reasoning engine.

    The reasoning engine acts as the primary public facade for the
    SciOS cognitive reasoning subsystem.

    It coordinates planning, inference, hypothesis generation,
    verification and state tracking while presenting a stable API to
    higher-level components.

    Notes
    -----
    The engine itself owns no domain knowledge.

    Knowledge is delegated to the underlying planner,
    inference engine and verifier.

    Thread Safety
    -------------
    Instances are not guaranteed to be thread-safe.

    They are intended to be lightweight and instantiated per runtime,
    workflow or agent.
    """

    __slots__ = (
        "_state",
        "_planner",
        "_inference",
        "_hypothesis",
        "_verifier",
        "_rules",
        "_running",
    )

    # ======================================================
    # Construction
    # ======================================================

    def __init__(self) -> None:
        """
        Create a new reasoning engine.
        """

        self._state = ReasoningState()

        self._planner = ReasoningPlanner()

        self._inference = InferenceEngine()

        self._hypothesis = HypothesisGenerator()

        self._verifier = ReasoningVerifier()

        self._rules: list[ReasoningRule] = []

        self._running: bool = True

    # ======================================================
    # Read-only Properties
    # ======================================================

    @property
    def planner(self) -> ReasoningPlanner:
        """
        Return the underlying planner.
        """

        return self._planner

    @property
    def inference_engine(self) -> InferenceEngine:
        """
        Return the inference engine.
        """

        return self._inference

    @property
    def hypothesis_generator(self) -> HypothesisGenerator:
        """
        Return the hypothesis generator.
        """

        return self._hypothesis

    @property
    def verifier(self) -> ReasoningVerifier:
        """
        Return the verifier.
        """

        return self._verifier

    @property
    def reasoning_state(self) -> ReasoningState:
        """
        Return the underlying reasoning state object.

        This exposes the complete state manager for advanced
        integrations while keeping the public ``state()`` API
        available for backward compatibility.
        """

        return self._state

    @property
    def rules(self) -> tuple[ReasoningRule, ...]:
        """
        Immutable view of registered reasoning rules.
        """

        return tuple(self._rules)

    @property
    def running(self) -> bool:
        """
        Whether the reasoning engine is active.
        """

        return self._running

    @property
    def rules_count(self) -> int:
        """
        Number of registered reasoning rules.
        """

        return len(self._rules)
# ==========================================================
# Part 2: Rule Management, Planning, Inference, Hypothesis
# ==========================================================

    # ------------------------------------------------------
    # Rule Management
    # ------------------------------------------------------

    @property
    def rules(self) -> list[dict[str, Any]]:
        """
        Read-only view of registered reasoning rules.
        """
        return list(self._rules)

    @property
    def rule_count(self) -> int:
        """
        Number of registered rules.
        """
        return len(self._rules)

    def add_rule(
        self,
        condition: str,
        conclusion: str,
    ) -> None:
        """
        Register a new inference rule.
        """
        self._rules.append(
            {
                "condition": condition,
                "conclusion": conclusion,
            }
        )

    def remove_rule(
        self,
        condition: str,
        conclusion: str | None = None,
    ) -> bool:
        """
        Remove the first matching rule.

        Returns
        -------
        bool
            True if a rule was removed.
        """
        for index, rule in enumerate(self._rules):
            if (
                rule["condition"] == condition
                and (
                    conclusion is None
                    or rule["conclusion"] == conclusion
                )
            ):
                del self._rules[index]
                return True

        return False

    def clear_rules(self) -> None:
        """
        Remove all rules.
        """
        self._rules.clear()

    def has_rule(
        self,
        condition: str,
        conclusion: str | None = None,
    ) -> bool:
        """
        Determine whether a rule exists.
        """
        return any(
            rule["condition"] == condition
            and (
                conclusion is None
                or rule["conclusion"] == conclusion
            )
            for rule in self._rules
        )

    # ------------------------------------------------------
    # Planning
    # ------------------------------------------------------

    def plan(
        self,
        goal: str | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate an execution plan.

        Accepts either a goal string or a goal dictionary.
        """
        if isinstance(goal, str):
            context = {"goal": goal}
            query = goal

        elif isinstance(goal, dict):
            context = dict(goal)

            query = str(
                context.get(
                    "query",
                    context.get(
                        "goal",
                        "",
                    ),
                )
            )

        else:
            raise TypeError(
                "plan() expects str or dict[str, Any]"
            )

        return self._planner.create_plan(
            query=query,
            context=context,
        )

    # ------------------------------------------------------
    # Inference
    # ------------------------------------------------------

    def infer(
        self,
        query_or_context: str | dict[str, Any],
    ) -> list[str] | dict[str, Any]:
        """
        Perform inference.

        Compatibility:

        - infer("query") -> inference dict
        - infer({...})   -> list[str]
        """

        # ------------------------------------------------------
        # Legacy API
        # ------------------------------------------------------

        if isinstance(query_or_context, dict):

            context = dict(query_or_context)

            query = str(
                context.get(
                    "query",
                    context.get(
                        "goal",
                        "reason",
                    ),
                )
            )

            inference = self._inference.infer(
                query=query,
                context=context,
            )

            conclusions: list[str] = []

            if "conclusion" in inference:
                conclusions.append(inference["conclusion"])

            for rule in self._rules:
                if rule["condition"] in context.values():
                    conclusions.append(rule["conclusion"])

            return conclusions

        # ------------------------------------------------------
        # Modern API
        # ------------------------------------------------------

        if isinstance(query_or_context, str):

            return self._inference.infer(
                query=query_or_context,
                context={},
            )

        raise TypeError(
            "infer() expects str or dict[str, Any]"
        )

    # ------------------------------------------------------
    # Hypothesis
    # ------------------------------------------------------

    def generate_hypotheses(
        self,
        goal: str | dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Generate candidate hypotheses.

        Backward compatible API.
        """

        if isinstance(goal, str):

            context = {"goal": goal}

            query = goal

        elif isinstance(goal, dict):

            context = dict(goal)

            query = str(
                context.get(
                    "query",
                    context.get(
                        "goal",
                        "",
                    ),
                )
            )

        else:
            raise TypeError(
                "generate_hypotheses() expects str or dict"
            )

        inference = self.infer(context)

        hypothesis = self._hypothesis.generate(
            query=query,
            inference=inference,
        )

        return [hypothesis]

    def select_best_hypothesis(
        self,
        hypotheses: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """
        Select the best hypothesis.

        Future versions may use confidence ranking.
        """
        if not hypotheses:
            return None

        return hypotheses[0]
# ==========================================================
# Part 3: Verification, Reasoning Pipeline, Lifecycle,
#         State, Status, Python Protocols
# ==========================================================

    # ------------------------------------------------------
    # Verification
    # ------------------------------------------------------

    def verify(
        self,
        hypothesis: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Verify a hypothesis.

        Returns
        -------
        bool
            True if the hypothesis is accepted.
        """

        result = self._verifier.verify(
            hypothesis=hypothesis,
            context=context or {},
        )

        return bool(
            result.get(
                "accepted",
                False,
            )
        )

    def verify_hypotheses(
        self,
        hypotheses: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Verify multiple hypotheses.

        The current implementation verifies the first
        hypothesis for backward compatibility.
        """

        if not hypotheses:

            return {
                "accepted": False,
                "details": "No hypotheses provided.",
            }

        return self._verifier.verify(
            hypothesis=hypotheses[0],
            context=context or {},
        )

    def evaluate_hypotheses(
        self,
        hypotheses: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Compatibility alias.
        """

        return self.verify_hypotheses(
            hypotheses,
            context,
        )

    # ------------------------------------------------------
    # Complete Reasoning Pipeline
    # ------------------------------------------------------

    def reason(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the complete reasoning pipeline.
        """

        context = dict(context or {})

        self._state.record(
            query=query,
            context=context,
        )

        plan = self.plan(
            {
                "goal": query,
                **context,
            }
        )

        inference = self.infer(
            {
                "query": query,
                **context,
            }
        )

        hypotheses = self.generate_hypotheses(
            {
                "query": query,
                **context,
            }
        )

        hypothesis = self.select_best_hypothesis(
            hypotheses
        )

        verification = self.verify_hypotheses(
            hypotheses,
            context,
        )

        accepted = bool(
            verification.get(
                "accepted",
                False,
            )
        )

        result = {
            "query": query,
            "plan": plan,
            "inference": inference,
            "hypothesis": hypothesis,
            "hypotheses": hypotheses,
            "verification": verification,
            "accepted": accepted,
        }

        self._state.record_result(result)

        return result

    def reason_about_goal(
        self,
        goal: dict[str, Any],
    ) -> list[str]:
        """
        Lightweight goal reasoning.
        """

        conclusions: list[str] = []

        if "goal" in goal:
            conclusions.append(
                f"Goal: {goal['goal']}"
            )

        if "event" in goal:
            conclusions.append(
                f"Event: {goal['event']}"
            )

        if goal.get("requirements"):
            conclusions.append(
                "Requirements: "
                + ", ".join(goal["requirements"])
            )

        if not conclusions:
            conclusions.append(
                "No goal information available."
            )

        return conclusions

    # ------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------

    def start(self) -> None:
        """
        Start the reasoning engine.
        """

        self._running = True

    def stop(self) -> None:
        """
        Stop the reasoning engine.
        """

        self._running = False

    def reset(self) -> None:
        """
        Reset the engine and all subcomponents.
        """

        self._state.reset()

        self._planner.reset()

        self._inference.reset()

        self._hypothesis.reset()

        self._verifier.reset()

        self._rules.clear()

        self._running = True

    # ------------------------------------------------------
    # State
    # ------------------------------------------------------

    @property
    def state(self) -> ReasoningState:
        """
        Return the reasoning state object.
        """

        return self._state

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    @property
    def running(self) -> bool:
        """
        Whether the engine is active.
        """

        return self._running

    def status(self) -> dict[str, Any]:
        """
        Runtime status.
        """

        return {
            "component": self.__class__.__name__,
            "running": self._running,
            "rules": len(self._rules),
            "planner": self._planner.status(),
            "inference": self._inference.status(),
            "hypothesis": self._hypothesis.status(),
            "verifier": self._verifier.status(),
            "state": self._state.status(),
        }

    # ------------------------------------------------------
    # Python Protocols
    # ------------------------------------------------------

    def __len__(self) -> int:
        """
        Number of registered rules.
        """

        return len(self._rules)

    def __bool__(self) -> bool:
        """
        Truth value of the engine.
        """

        return self._running

    def __contains__(
        self,
        condition: str,
    ) -> bool:
        """
        Membership test for rule conditions.
        """

        return any(
            rule["condition"] == condition
            for rule in self._rules
        )

    def __iter__(self):
        """
        Iterate over registered rules.
        """

        return iter(self._rules)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"running={self._running}, "
            f"rules={len(self._rules)}, "
            f"records={self._state.status()['records']})"
        )

    def __str__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(running={self._running}, "
            f"rules={len(self._rules)})"
        )                