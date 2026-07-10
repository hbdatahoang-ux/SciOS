# scios/cognitive_core/reflection/reflection.py

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
"""

from __future__ import annotations

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


class ReflectionEngine:
    """
    ReflectionEngine orchestrates the reflection pipeline.
    """

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

    def reflect(
        self,
        execution_result: dict,
        reasoning_trace: dict | None = None,
        plan: dict | None = None,
    ) -> dict:
        """
        Run the full reflection pipeline on an execution result.
        """
        self.state.set_state("reflecting")
        self.recorder.log("Reflection started")

        evaluation = self.evaluator.evaluate(execution_result)
        critique = self.critic.analyze(evaluation)
        analysis = self.analyzer.analyze(reasoning_trace, plan, execution_result)
        metrics = self.metrics.compute(execution_result, analysis)
        score = self.scorer.score(metrics)
        improvements = self.improvement.suggest(analysis, critique, score)
        feedback = self.feedback.generate(improvements)
        report = self.reporter.generate(
            evaluation, critique, analysis, metrics, score, feedback
        )

        self.history.store(report)
        self.adaptive.apply(improvements)

        self.state.set_state("completed")
        self.recorder.log("Reflection completed")

        return report

    def status(self) -> dict:
        """
        Return current reflection status.
        """
        return {
            "state": self.state.get_state(),
            "history_count": len(self.history.entries),
        }

    def reset(self) -> None:
        """
        Reset reflection state and clear history/logs.
        """
        self.state.reset()
        self.history.clear()
        self.recorder.clear()
