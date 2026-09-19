from __future__ import annotations

import pandas as pd

from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.planner import Planner
from scios.cognitive_core.planner.task import Task
from scios.compilation.plan_compiler import PlanCompiler
from scios.execution.operation.ref import OperationRef
from scios.execution.operation.registry import OperationRegistry
from scios.execution.operation.resolver import OperationResolver
from scios.runtime.executor import Executor
from scios.runtime.tools.result import ToolResult


CSV_REF = OperationRef("csv_analysis", "0.1.0")


def test_csv_goal_executes_through_cognitive_to_runtime_boundary(
    tmp_path,
):
    csv_path = tmp_path / "dataset.csv"

    dataframe = pd.DataFrame(
        {
            "value": [10, 11, 12, 13, 14, 100],
        }
    )
    dataframe.to_csv(csv_path, index=False)

    goal = Goal(
        description="Analyze CSV anomalies",
        success_criteria=["csv_analysis_completed"],
    )

    planner = Planner()

    plan = planner.create_plan(
        goal,
        tasks=[
            Task(
                description="Analyze CSV dataset",
                task_id="csv-analysis",
            )
        ],
    )

    assert plan.goal is goal
    assert len(plan.tasks) == 1

    # Application-level binding seam.
    #
    # This is intentionally RED until the CSV application adapter
    # exists. The cognitive Task must not carry file_path.
    from scios.application.csv_analysis import CSVAnalysisApplication

    application = CSVAnalysisApplication(
        file_path=str(csv_path),
    )

    binder = application.binder
    registry = application.registry

    compiler = PlanCompiler(
        operation_binder=binder,
    )

    resolver = OperationResolver(registry)

    service = application.execution_service(
        planner=planner,
        compiler=compiler,
        resolver=resolver,
        executor=Executor(),
    )

    result = service.execute(
        goal,
        tasks=plan.tasks,
    )

    assert result.goal is goal
    assert len(result.graph.nodes) == 1

    node = next(iter(result.graph.nodes.values()))

    assert node.operation_ref == CSV_REF
    assert node.status.name == "SUCCESS"

    operation_result = application.last_result

    assert isinstance(operation_result, ToolResult)
    assert operation_result.success is True

    value = operation_result.value

    assert value["rows"] == 6
    assert value["columns"] == 1
    assert value["outliers"]["value"]["count"] == 1
    assert value["outliers"]["value"]["indices"] == [5]
