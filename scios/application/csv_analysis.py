from __future__ import annotations

from typing import Any

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.compilation.operation_binder import OperationBinder
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor
from scios.runtime.tools.csv_analysis import CSVAnalysisTool
from scios.runtime.tools.result import ToolResult

from .csv_reasoning import EvidenceDeductiveStrategy
from .goal_execution import (
    GoalExecutionResult,
    GoalExecutionService,
    build_goal_execution_service,
)
from .natural_language import DeterministicNaturalLanguageReasoner


CSV_ANALYSIS_REF = OperationRef(
    "csv_analysis",
    "0.1.0",
)


class CSVAnalysisBinder(OperationBinder):
    """Bind the CSV analysis cognitive task to its execution operation."""

    def bind(self, task: Task) -> OperationRef | None:
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")

        if task.id != "csv-analysis":
            return None

        return CSV_ANALYSIS_REF


class CSVAnalysisApplication:
    """
    Application orchestration for CSV anomaly analysis.

    The application composes existing frozen contracts:

        Goal
          -> Planner
          -> Plan
          -> PlanCompiler
          -> ExecutionGraph
          -> ExecutionRunner
          -> CSVAnalysisTool
          -> evidence
          -> EvidenceDeductiveStrategy
          -> ReasoningResult
          -> final answer

    No core runtime or cognitive contract is modified here.
    """

    def __init__(self, *, file_path: str) -> None:
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string")

        if not file_path.strip():
            raise ValueError("file_path must not be empty")

        self.file_path = file_path
        self.tool = CSVAnalysisTool()
        self.registry = OperationRegistry()
        self.binder = CSVAnalysisBinder()
        self.reasoner = DeterministicNaturalLanguageReasoner()
        self.last_result: ToolResult | None = None

        self._register_operations()

    def _register_operations(self) -> None:
        def csv_analysis_operation() -> ToolResult:
            result = self.tool.run(
                file_path=self.file_path,
            )
            self.last_result = result
            return result

        self.registry.register(
            CSV_ANALYSIS_REF,
            csv_analysis_operation,
        )

    def execution_service(
        self,
        *,
        planner: Planner | None = None,
        compiler: PlanCompiler | None = None,
        resolver: OperationResolver | None = None,
        executor: Executor | None = None,
    ) -> GoalExecutionService:
        """Build the shared goal-execution composition."""
        return build_goal_execution_service(
            binder=self.binder,
            registry=self.registry,
            planner=planner,
            compiler=compiler,
            resolver=resolver,
            executor=executor,
        )

    def reasoning_problem(
        self,
        *,
        query: str,
        evidence: dict[str, object],
    ) -> ReasoningProblem:
        """Build a reasoning problem from deterministic tool evidence."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        if not isinstance(evidence, dict):
            raise TypeError("evidence must be a dict")

        return ReasoningProblem(
            query=query,
            context={
                "evidence": dict(evidence),
            },
        )

    def analyze(
        self,
        *,
        goal: Goal,
        query: str,
    ) -> dict[str, object]:
        """
        Execute the complete CSV product vertical slice.

        Returns a minimal application-level answer representation.
        """
        if not isinstance(goal, Goal):
            raise TypeError("goal must be a Goal")

        execution_service = self.execution_service()

        task = Task(
            "Analyze CSV dataset for anomalies.",
            task_id="csv-analysis",
        )

        execution = execution_service.execute(
            goal,
            tasks=[task],
        )

        if self.last_result is None:
            raise RuntimeError(
                "CSV analysis execution produced no ToolResult."
            )

        if not self.last_result.success:
            error = self.last_result.error
            raise RuntimeError(
                "CSV analysis execution failed."
            ) from error

        evidence_payload = self.last_result.value

        if not isinstance(evidence_payload, dict):
            raise TypeError(
                "CSV analysis tool returned invalid evidence."
            )

        anomalies = evidence_payload["outliers"]

        reasoning_results: list[ReasoningResult] = []

        for _, outlier_data in anomalies.items():
            if not isinstance(outlier_data, dict):
                continue

            evidence_items = outlier_data.get("evidence", [])

            for evidence in evidence_items:
                problem = self.reasoning_problem(
                    query=query,
                    evidence=evidence,
                )

                reasoning_results.append(
                    EvidenceDeductiveStrategy().execute(problem)
                )

        try:
            explanation = self.reasoner.explain(
                query=query,
                evidence=evidence_payload,
                reasoning=[
                    result.conclusion
                    for result in reasoning_results
                ],
            )
        except Exception:
            explanation = self._deterministic_fallback_explanation(
                evidence=evidence_payload,
                reasoning=reasoning_results,
            )

        answer = self._build_answer(
            goal=goal,
            execution=execution,
            evidence=evidence_payload,
            reasoning=reasoning_results,
            explanation=explanation,
        )

        return answer

    @staticmethod
    def _deterministic_fallback_explanation(
        *,
        evidence: dict[str, object],
        reasoning: list[ReasoningResult],
    ) -> str:
        anomaly_count = sum(
            1
            for result in reasoning
            if result.conclusion.get("is_outlier") is True
        )

        if anomaly_count == 0:
            return (
                "No anomalous numeric values were identified using the "
                "available deterministic evidence."
            )

        return (
            f"{anomaly_count} anomalous numeric value(s) were identified "
            "by the deterministic reasoning layer."
        )


    def _build_answer(
        self,
        *,
        goal: Goal,
        execution: GoalExecutionResult,
        evidence: dict[str, object],
        reasoning: list[ReasoningResult],
        explanation: str,
    ) -> dict[str, object]:
        """Build the minimal user-facing application result."""
        return {
            "goal": goal.description,
            "rows": evidence["rows"],
            "columns": evidence["columns"],
            "column_names": evidence["column_names"],
            "missing": evidence["missing"],
            "outliers": evidence["outliers"],
            "reasoning": [
                result.conclusion
                for result in reasoning
            ],
            "explanation": explanation,
        }
