from __future__ import annotations

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.task import Task
from scios.compilation.operation_binder import OperationBinder
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor
from scios.runtime.tools.dataset_quality import DatasetQualityTool
from scios.runtime.tools.result import ToolResult

from .goal_execution import (
    GoalExecutionService,
    build_goal_execution_service,
)


DATASET_QUALITY_REF = OperationRef(
    "dataset_quality",
    "0.1.0",
)


class DatasetQualityBinder(OperationBinder):
    """Bind the dataset-quality cognitive task to its operation."""

    def bind(self, task: Task) -> OperationRef | None:
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")

        if task.id != "dataset-quality":
            return None

        return DATASET_QUALITY_REF


class DatasetQualityApplication:
    """Application orchestration for deterministic dataset quality audit."""

    def __init__(self, *, file_path: str) -> None:
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string")

        if not file_path.strip():
            raise ValueError("file_path must not be empty")

        self.file_path = file_path
        self.tool = DatasetQualityTool()
        self.registry = OperationRegistry()
        self.binder = DatasetQualityBinder()
        self.last_result: ToolResult | None = None

        self._register_operations()

    def _register_operations(self) -> None:
        def dataset_quality_operation() -> ToolResult:
            result = self.tool.run(
                file_path=self.file_path,
            )
            self.last_result = result
            return result

        self.registry.register(
            DATASET_QUALITY_REF,
            dataset_quality_operation,
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

    def analyze(
        self,
        *,
        goal: Goal,
    ) -> dict[str, object]:
        """Execute the dataset quality workflow and return measured evidence."""
        if not isinstance(goal, Goal):
            raise TypeError("goal must be a Goal")

        self.execution_service().execute(
            goal,
            tasks=[
                Task(
                    "Audit dataset structural and integrity quality.",
                    task_id="dataset-quality",
                )
            ],
        )

        if self.last_result is None:
            raise RuntimeError(
                "Dataset quality execution produced no ToolResult."
            )

        if not self.last_result.success:
            error = self.last_result.error
            raise RuntimeError(
                "Dataset quality execution failed."
            ) from error

        evidence = self.last_result.value

        if not isinstance(evidence, dict):
            raise TypeError(
                "Dataset quality tool returned invalid evidence."
            )

        return dict(evidence)

