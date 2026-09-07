"""
SciOS Plan Compiler
===================

Semantic compiler at the boundary between the Cognitive Planner
and the Execution IR.

Canonical transformation:

    Cognitive Plan
        |
        | semantic lowering
        v
    ExecutionGraph

Responsibilities
----------------
- Validate the input Plan.
- Lower each cognitive Task to one ExecutionNode.
- Lower Task dependencies to ExecutionEdges.
- Preserve cognitive-task provenance.
- Preserve selected execution-relevant metadata.

Non-responsibilities
--------------------
- Runtime execution.
- Scheduling.
- Dispatch.
- Tool invocation.
- Runtime callable resolution.
- Retry or recovery.
"""

from __future__ import annotations

from typing import Any

from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.task import Task

from scios.execution.graph.graph import ExecutionGraph
from scios.execution.graph.edge import ExecutionEdge
from scios.execution.node.kind import NodeKind
from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus

from .errors import (
    CyclicPlanError,
    InvalidPlanError,
    MissingTaskDependencyError,
    UnsupportedTaskError,
)


__all__ = [
    "PlanCompiler",
]


class PlanCompiler:
    """
    Compile a cognitive Plan into an ExecutionGraph.

    This class is deliberately a pure semantic compiler.

    It does not execute, schedule, dispatch, or resolve runtime
    operations.
    """

    def compile(self, plan: Plan) -> ExecutionGraph:
        """
        Compile a cognitive Plan into an ExecutionGraph.

        Parameters
        ----------
        plan:
            Canonical cognitive-core Plan.

        Returns
        -------
        ExecutionGraph
            Execution IR containing one node per Task and one edge
            per Task dependency.

        Raises
        ------
        InvalidPlanError
            If the input is not a valid Plan or is structurally invalid.

        MissingTaskDependencyError
            If a Task dependency cannot be resolved to another Task.

        UnsupportedTaskError
            If a Task cannot be lowered to an ExecutionNode.

        CyclicPlanError
            If the planning graph contains a cycle.
        """
        self._validate_plan(plan)

        try:
            plan.task_graph.topological_sort()
        except Exception as exc:
            message = str(exc)

            if "cycle" in message.lower():
                raise CyclicPlanError(
                    "Cannot compile a cyclic cognitive Plan."
                ) from exc

            raise InvalidPlanError(
                f"Invalid cognitive Plan graph: {message}"
            ) from exc

        graph = ExecutionGraph()

        # Planning identity -> runtime execution identity.
        task_to_node_id: dict[str, Any] = {}

        # ----------------------------------------------------------
        # Phase 1: Task -> ExecutionNode
        # ----------------------------------------------------------

        for task in plan.tasks:
            node = self._compile_task(task)

            graph.add_node(node)

            if task.id is not None:
                if task.id in task_to_node_id:
                    raise InvalidPlanError(
                        f"Duplicate Task id: {task.id!r}"
                    )

                task_to_node_id[task.id] = node.node_id

        # ----------------------------------------------------------
        # Phase 2: dependency -> ExecutionEdge
        #
        # Cognitive representation:
        #
        #     B.dependencies = ["A"]
        #
        # Execution representation:
        #
        #     A -> B
        # ----------------------------------------------------------

        for task in plan.tasks:
            if task.id is None:
                if task.dependencies:
                    raise MissingTaskDependencyError(
                        "A Task with no id cannot have dependencies."
                    )
                continue

            target_id = task_to_node_id[task.id]

            for dependency_id in task.dependencies:
                try:
                    source_id = task_to_node_id[dependency_id]
                except KeyError as exc:
                    raise MissingTaskDependencyError(
                        f"Task {task.id!r} depends on unknown "
                        f"Task {dependency_id!r}."
                    ) from exc

                if source_id == target_id:
                    raise CyclicPlanError(
                        f"Task {task.id!r} cannot depend on itself."
                    )

                graph.add_edge(
                    ExecutionEdge(
                        source_id=source_id,
                        target_id=target_id,
                        label="dependency",
                    )
                )

        return graph

    # ==============================================================
    # Validation
    # ==============================================================

    @staticmethod
    def _validate_plan(plan: Plan) -> None:
        """Validate the basic input boundary."""

        if not isinstance(plan, Plan):
            raise InvalidPlanError(
                "PlanCompiler.compile() requires "
                "scios.cognitive_core.planner.Plan."
            )

        if not isinstance(plan.tasks, list):
            raise InvalidPlanError(
                "Plan.tasks must be a list."
            )

        for index, task in enumerate(plan.tasks):
            if not isinstance(task, Task):
                raise InvalidPlanError(
                    f"Plan.tasks[{index}] is not a Task."
                )

    # ==============================================================
    # Task lowering
    # ==============================================================

    @staticmethod
    def _compile_task(task: Task) -> ExecutionNode:
        """
        Lower one cognitive Task to one ExecutionNode.

        Semantic mapping:

            Task.description
                -> ExecutionNode.name

            Task.id
                -> metadata.source.task_id

            Task
                -> NodeKind.PROCESS

            compilation
                -> NodeStatus.READY
        """

        if not isinstance(task, Task):
            raise UnsupportedTaskError(
                f"Unsupported planning object: {type(task).__name__}"
            )

        metadata: dict[str, Any] = {
            "source": {
                "type": "cognitive_task",
                "task_id": task.id,
            },
            "task_metadata": dict(task.metadata),
        }

        # Priority is an execution-relevant planning attribute.
        if "priority" in task.constraints:
            metadata["priority"] = task.constraints["priority"]

        return ExecutionNode(
            kind=NodeKind.PROCESS,
            status=NodeStatus.READY,
            name=task.description,
            metadata=metadata,
        )