from __future__ import annotations

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.reasoning.core.problem import ReasoningProblem
from scios.cognitive_core.reasoning.core.result import ReasoningResult
from scios.cognitive_core.reasoning.core.step import ReasoningStep
from scios.cognitive_core.reasoning.core.types import ReasoningType
from scios.compilation.operation_binder import OperationBinder
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor
from scios.runtime.tools.result import ToolResult
from scios.runtime.tools.time_series import TimeSeriesChangeTool

from .goal_execution import GoalExecutionResult, GoalExecutionService


TIME_SERIES_CHANGE_REF = OperationRef(
    "time_series_change",
    "0.1.0",
)


class TimeSeriesChangeBinder(OperationBinder):
    """Application-level binding from cognitive Task to time-series operation."""

    def bind(self, task: Task) -> OperationRef | None:
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")

        if task.id != "time-series-change":
            return None

        return TIME_SERIES_CHANGE_REF


class TimeSeriesChangeApplication:
    """Application orchestration for the time-series change product."""

    def __init__(self, *, file_path: str) -> None:
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string")

        if not file_path.strip():
            raise ValueError("file_path must not be empty")

        self.file_path = file_path
        self.tool = TimeSeriesChangeTool()
        self.registry = OperationRegistry()
        self.binder = TimeSeriesChangeBinder()
        self.last_result: ToolResult | None = None

        self._register_operations()

    def _register_operations(self) -> None:
        def time_series_change_operation() -> ToolResult:
            result = self.tool.run(file_path=self.file_path)
            self.last_result = result
            return result

        self.registry.register(
            TIME_SERIES_CHANGE_REF,
            time_series_change_operation,
        )

    def execution_service(
        self,
        *,
        planner: Planner | None = None,
        compiler: PlanCompiler | None = None,
        resolver: OperationResolver | None = None,
        executor: Executor | None = None,
    ) -> GoalExecutionService:
        if planner is None:
            planner = Planner()

        if compiler is None:
            compiler = PlanCompiler(
                operation_binder=self.binder,
            )

        if resolver is None:
            resolver = OperationResolver(self.registry)

        if executor is None:
            executor = Executor()

        return GoalExecutionService(
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
        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "query must be a non-empty string"
            )

        if not isinstance(evidence, dict):
            raise TypeError("evidence must be a dict")

        return ReasoningProblem(
            query=query,
            reasoning_type=ReasoningType.DEDUCTIVE,
            context={
                "evidence": dict(evidence),
            },
        )

    @staticmethod
    def _reason_about_change(
        problem: ReasoningProblem,
    ) -> ReasoningResult:
        if not isinstance(problem, ReasoningProblem):
            raise TypeError(
                "problem must be a ReasoningProblem"
            )

        evidence = problem.context.get("evidence")

        if not isinstance(evidence, dict):
            raise ValueError(
                "Reasoning problem requires evidence."
            )

        required = {
            "timestamp",
            "previous_timestamp",
            "previous_value",
            "value",
            "delta",
            "absolute_delta",
            "relative_change",
            "direction",
            "significant_change",
            "q1_delta",
            "q3_delta",
            "iqr_delta",
            "upper_delta_bound",
            "rule",
        }

        missing = required - set(evidence)

        if missing:
            raise ValueError(
                "Time-series evidence is missing required fields: "
                + ", ".join(sorted(missing))
            )

        significant = evidence["significant_change"] is True

        if significant:
            conclusion = {
                "timestamp": evidence["timestamp"],
                "previous_timestamp": evidence[
                    "previous_timestamp"
                ],
                "previous_value": evidence["previous_value"],
                "value": evidence["value"],
                "delta": evidence["delta"],
                "absolute_delta": evidence["absolute_delta"],
                "relative_change": evidence[
                    "relative_change"
                ],
                "direction": evidence["direction"],
                "significant_change": True,
                "evidence": dict(evidence),
            }

            description = (
                "The transition is classified as a significant "
                "change by deterministic IQR delta evidence."
            )
        else:
            conclusion = {
                "timestamp": evidence["timestamp"],
                "previous_timestamp": evidence[
                    "previous_timestamp"
                ],
                "previous_value": evidence["previous_value"],
                "value": evidence["value"],
                "delta": evidence["delta"],
                "absolute_delta": evidence["absolute_delta"],
                "relative_change": evidence[
                    "relative_change"
                ],
                "direction": evidence["direction"],
                "significant_change": False,
                "evidence": dict(evidence),
            }

            description = (
                "The transition is not classified as a "
                "significant change by deterministic IQR delta "
                "evidence."
            )

        step = ReasoningStep(
            description=description,
        )

        return ReasoningResult(
            problem=problem,
            steps=[step],
            conclusion=conclusion,
            accepted=True,
            metadata={
                "confidence": 1.0,
                "confidence_basis": (
                    "deterministic IQR delta evidence"
                ),
            },
        )

    @staticmethod
    def _explain_changes(
        *,
        query: str,
        evidence: dict[str, object],
        reasoning: list[ReasoningResult],
    ) -> str:
        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "query must be a non-empty string"
            )

        if not isinstance(evidence, dict):
            raise TypeError("evidence must be a dict")

        if not reasoning:
            rows = evidence.get("rows")
            columns = evidence.get("columns")

            if rows is not None and columns is not None:
                return (
                    "No significant changes were identified in "
                    f"the time series ({rows} rows, {columns} "
                    "columns) using the available deterministic "
                    "IQR delta evidence."
                )

            return (
                "No significant changes were identified using "
                "the available deterministic IQR delta evidence."
            )

        if len(reasoning) == 1:
            item = reasoning[0].conclusion
            return (
                "A significant change was identified: "
                f"{item['previous_value']} → {item['value']} "
                f"({item['direction']}, Δ={item['delta']}) "
                f"at {item['timestamp']}, classified using the "
                f"{item['evidence']['rule']} rule."
            )

        parts: list[str] = []

        for result in reasoning:
            item = result.conclusion
            parts.append(
                f"{item['previous_value']} → {item['value']} "
                f"(Δ={item['delta']}, {item['direction']}) "
                f"at {item['timestamp']}"
            )

        return (
            f"{len(reasoning)} significant changes were identified: "
            + "; ".join(parts)
            + "."
        )

    @staticmethod
    def _deterministic_fallback_explanation(
        *,
        evidence: dict[str, object],
        reasoning: list[ReasoningResult],
    ) -> str:
        changes = len(reasoning)

        if changes == 0:
            return (
                "No significant changes were identified using "
                "the available deterministic IQR delta evidence."
            )

        return (
            f"{changes} significant change(s) were identified "
            "by the deterministic reasoning layer."
        )

    def analyze(
        self,
        *,
        goal: Goal,
        query: str,
    ) -> dict[str, object]:
        if not isinstance(goal, Goal):
            raise TypeError("goal must be a Goal")

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "query must be a non-empty string"
            )

        execution_service = self.execution_service()

        task = Task(
            "Analyze time series for significant changes.",
            task_id="time-series-change",
        )

        execution = execution_service.execute(
            goal,
            tasks=[task],
        )

        if self.last_result is None:
            raise RuntimeError(
                "Time-series change execution produced no "
                "ToolResult."
            )

        if not self.last_result.success:
            error = self.last_result.error
            raise RuntimeError(
                "Time-series change execution failed."
            ) from error

        evidence_payload = self.last_result.value

        if not isinstance(evidence_payload, dict):
            raise TypeError(
                "Time-series change tool returned invalid evidence."
            )

        transitions = evidence_payload.get("transitions", [])

        if not isinstance(transitions, list):
            raise TypeError(
                "Time-series change evidence contains invalid "
                "transitions."
            )

        reasoning_results: list[ReasoningResult] = []

        for transition in transitions:
            if not isinstance(transition, dict):
                continue

            problem = self.reasoning_problem(
                query=query,
                evidence=transition,
            )

            reasoning_results.append(
                self._reason_about_change(problem)
            )

        significant_reasoning = [
            result
            for result in reasoning_results
            if result.conclusion.get("significant_change")
            is True
        ]

        try:
            explanation = self._explain_changes(
                query=query,
                evidence=evidence_payload,
                reasoning=significant_reasoning,
            )
        except Exception:
            explanation = self._deterministic_fallback_explanation(
                evidence=evidence_payload,
                reasoning=significant_reasoning,
            )

        return self._build_answer(
            goal=goal,
            execution=execution,
            evidence=evidence_payload,
            reasoning=significant_reasoning,
            explanation=explanation,
        )

    @staticmethod
    def _build_answer(
        *,
        goal: Goal,
        execution: GoalExecutionResult,
        evidence: dict[str, object],
        reasoning: list[ReasoningResult],
        explanation: str,
    ) -> dict[str, object]:
        return {
            "goal": goal.description,
            "rows": evidence["rows"],
            "columns": evidence["columns"],
            "column_names": evidence["column_names"],
            "timestamp_column": evidence[
                "timestamp_column"
            ],
            "value_column": evidence["value_column"],
            "time_start": evidence["time_start"],
            "time_end": evidence["time_end"],
            "q1_delta": evidence["q1_delta"],
            "q3_delta": evidence["q3_delta"],
            "iqr_delta": evidence["iqr_delta"],
            "upper_delta_bound": evidence[
                "upper_delta_bound"
            ],
            "transitions": evidence["transitions"],
            "changes": evidence["changes"],
            "reasoning": [
                result.conclusion
                for result in reasoning
            ],
            "explanation": explanation,
        }
