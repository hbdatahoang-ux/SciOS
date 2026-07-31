"""
SciOS Reflection Engine
=======================

Orchestrates the metacognition pipeline:

- Evaluate execution results
- Criticize weaknesses
- Analyze reasoning & planning
- Compute metrics
- Score quality
- Suggest improvements
- Generate feedback
- Produce reflection report
- Update history & adaptive policy

Python 3.11+
"""

from __future__ import annotations

from typing import Any


from .evaluator import Evaluator
from .critic import Critic
from .analyzer import Analyzer
from .metrics import Metrics
from .scorer import Scorer
from .improvement import Improvement
from .feedback import Feedback
from .report import ReflectionReport
from .history import ReflectionHistory
from .recorder import ReflectionRecorder
from .state import ReflectionState
from .adaptive import AdaptivePolicy


__all__ = [
    "ReflectionEngine",
]


class ReflectionEngine:
    """
    ReflectionEngine.

    Provides a complete metacognitive reflection pipeline.

    Pipeline:

        Execution Result
              |
              v
          Evaluator
              |
              v
           Critic
              |
              v
          Analyzer
              |
              v
           Metrics
              |
              v
           Scorer
              |
              v
       Improvement Generator
              |
              v
          Feedback
              |
              v
       Reflection Report

    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(self) -> None:

        self.evaluator = Evaluator()

        self.critic = Critic()

        self.analyzer = Analyzer()

        self.metrics = Metrics()

        self.scorer = Scorer()

        self.improvement = Improvement()

        self.feedback = Feedback()

        self.reporter = ReflectionReport()

        self.history = ReflectionHistory()

        self.recorder = ReflectionRecorder()

        self.state = ReflectionState()

        self.adaptive = AdaptivePolicy()


    # ======================================================
    # Main Reflection Pipeline
    # ======================================================

    def reflect(
        self,
        execution_result: dict[str, Any],
        reasoning_trace: dict[str, Any] | None = None,
        plan: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute complete reflection pipeline.
        """

        self.state.set_state(
            "reflecting"
        )

        self.recorder.log(
            "Reflection started"
        )


        evaluation = (
            self.evaluator.evaluate(
                execution_result
            )
        )


        critique = (
            self.critic.analyze(
                evaluation
            )
        )


        analysis = (
            self.analyzer.analyze(
                reasoning_trace or {},
                plan or {},
                execution_result,
            )
        )


        metrics = (
            self.metrics.compute(
                execution_result,
                analysis,
            )
        )


        score = (
            self.scorer.score(
                metrics
            )
        )


        improvements = (
            self.improvement.suggest(
                analysis,
                critique,
                score,
            )
        )


        feedback = (
            self.feedback.generate(
                improvements
            )
        )


        report = (
            self.reporter.generate(
                evaluation,
                critique,
                analysis,
                metrics,
                score,
                feedback,
            )
        )


        self.history.store(
            report
        )


        self.adaptive.apply(
            improvements
        )


        self.state.set_state(
            "completed"
        )


        self.recorder.log(
            "Reflection completed"
        )


        return report


    # ======================================================
    # Backward Compatible API
    # ======================================================

    def run(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute reflection from unified payload.

        Expected input:

        {
            "execution_result": {},
            "reasoning": {},
            "plan": {}
        }

        """

        return self.reflect(

            execution_result=data.get(
                "execution_result",
                {},
            ),

            reasoning_trace=data.get(
                "reasoning",
                {},
            ),

            plan=data.get(
                "plan",
                {},
            ),
        )


    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Return reflection runtime status.
        """

        return {

            "state":
                self.state.get_state(),

            "history_count":
                len(
                    self.history.entries
                ),

        }


    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(
        self,
    ) -> None:
        """
        Reset reflection engine.
        """

        self.state.reset()

        self.history.clear()

        self.recorder.clear()


    # ======================================================
    # Python Protocols
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            "("
            f"state={self.state.get_state()}, "
            f"history={len(self.history.entries)}"
            ")"
        )