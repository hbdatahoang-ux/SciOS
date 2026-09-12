from __future__ import annotations

from typing import Any

from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.task import Task

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.graph.edge import ExecutionEdge
from scios.execution.node.kind import NodeKind
from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus

from .operation_binder import OperationBinder
from .errors import (
    CyclicPlanError,
    InvalidPlanError,
    MissingTaskDependencyError,
    UnsupportedTaskError,
)

__all__ = ["PlanCompiler"]


class PlanCompiler:
    """Compile a cognitive Plan into an ExecutionGraph."""

    def __init__(
        self,
        operation_binder: OperationBinder | None = None,
    ) -> None:
        self._operation_binder = operation_binder

    def compile(self, plan: Plan) -> ExecutionGraph:
        self._validate_plan(plan)

        try:
            plan.task_graph.topological_sort()
        except Exception as exc:
            message = str(exc)

            if "unknown dependency" in message.lower():
                raise MissingTaskDependencyError(
                    f"Invalid cognitive Plan graph: {message}"
                ) from exc

            if "cycle" in message.lower():
                raise CyclicPlanError(
                    "Cannot compile a cyclic cognitive Plan."
                ) from exc

            raise InvalidPlanError(
                f"Invalid cognitive Plan graph: {message}"
            ) from exc

        graph = ExecutionGraph()
        task_to_node_id: dict[str, Any] = {}

        for task in plan.tasks:
            node = self._compile_task(task)
            graph.add_node(node)

            if task.id is not None:
                if task.id in task_to_node_id:
                    raise InvalidPlanError(
                        f"Duplicate Task id: {task.id!r}"
                    )

                task_to_node_id[task.id] = node.node_id

        for task_id, dependency_ids in plan.task_graph.edges.items():
            try:
                target_id = task_to_node_id[task_id]
            except KeyError as exc:
                raise MissingTaskDependencyError(
                    f"TaskGraph contains unknown Task {task_id!r}."
                ) from exc

            for dependency_id in dependency_ids:
                try:
                    source_id = task_to_node_id[dependency_id]
                except KeyError as exc:
                    raise MissingTaskDependencyError(
                        f"Task {task_id!r} depends on unknown "
                        f"Task {dependency_id!r}."
                    ) from exc

                if source_id == target_id:
                    raise CyclicPlanError(
                        f"Task {task_id!r} cannot depend on itself."
                    )

                graph.add_edge(
                    ExecutionEdge(
                        source_id=source_id,
                        target_id=target_id,
                        relation="dependency",
                    )
                )

        return graph

    @staticmethod
    def _validate_plan(plan: Plan) -> None:
        if not isinstance(plan, Plan):
            raise InvalidPlanError(
                "PlanCompiler.compile() requires "
                "scios.cognitive_core.planner.Plan."
            )

        if not isinstance(plan.tasks, list):
            raise InvalidPlanError("Plan.tasks must be a list.")

        for index, task in enumerate(plan.tasks):
            if not isinstance(task, Task):
                raise InvalidPlanError(
                    f"Plan.tasks[{index}] is not a Task."
                )

    def _compile_task(self, task: Task) -> ExecutionNode:
        if not isinstance(task, Task):
            raise UnsupportedTaskError(
                f"Unsupported planning object: {type(task).__name__}"
            )

        operation_ref = None

        if self._operation_binder is not None:
            operation_ref = self._operation_binder.bind(task)

        metadata: dict[str, Any] = {
            "source": {
                "type": "cognitive_task",
                "task_id": task.id,
            },
            "task_metadata": dict(task.metadata),
        }

        if "priority" in task.constraints:
            metadata["priority"] = task.constraints["priority"]

        return ExecutionNode(
            kind=NodeKind.PROCESS,
            status=NodeStatus.READY,
            name=task.description,
            operation_ref=operation_ref,
            metadata=metadata,
        )
