from __future__ import annotations

from scios.cognitive_core.planner.task import Task
from scios.compilation.operation_binder import OperationBinder
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor
from scios.runtime.tools.csv_analysis import CSVAnalysisTool
from scios.runtime.tools.result import ToolResult

from .goal_execution import GoalExecutionResult, GoalExecutionService


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
    Application adapter for the CSV anomaly-analysis use case.

    This class connects the generic cognitive/execution boundary to the
    existing CSVAnalysisTool without modifying any core contract.
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
        planner,
        compiler: PlanCompiler,
        resolver: OperationResolver,
        executor: Executor,
    ) -> GoalExecutionService:
        return GoalExecutionService(
            planner=planner,
            compiler=compiler,
            resolver=resolver,
            executor=executor,
        )
