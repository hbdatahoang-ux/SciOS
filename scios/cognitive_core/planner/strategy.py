"""
SciOS Cognitive Core Planning Strategy
======================================

Strategy abstraction for the canonical SciOS cognitive planner.

A planning strategy transforms planning objects only. It does not
execute tasks, schedule runtime work, or resolve runtime operations.
"""

from __future__ import annotations

from .goal import Goal
from .plan import Plan
from .task import Task

__all__ = [
    "PlanningStrategy",
]


class PlanningStrategy:
    """
    Default cognitive planning strategy.

    Responsibilities
    ----------------
    - Decompose a Goal into planning Tasks.
    - Apply planning metadata to a Plan.
    - Preserve the cognitive planning model.

    Non-responsibilities
    --------------------
    - Runtime execution
    - Scheduling
    - Tool invocation
    - Runtime state management
    - ExecutionGraph construction
    """

    def __init__(
        self,
        name: str = "DefaultStrategy",
        description: str = "",
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not isinstance(description, str):
            raise TypeError("description must be a string")

        if not name:
            raise ValueError("name must not be empty")

        self.name = name
        self.description = description

    def apply(self, plan: Plan) -> Plan:
        """
        Apply this strategy to a Plan.

        Returns a new Plan and never mutates the input Plan.

        The default strategy preserves:
        - the Goal
        - the Tasks
        - the TaskGraph topology
        - the ConstraintSet
        - existing metadata

        It additionally records the selected strategy name in metadata.
        """
        if not isinstance(plan, Plan):
            raise TypeError("plan must be an instance of Plan")

        new_plan = Plan(
            goal=plan.goal,
            tasks=list(plan.tasks),
            task_graph=plan.task_graph,
            constraints=plan.constraints,
        )

        new_plan.constraints = plan.constraints
        new_plan.metadata = dict(plan.metadata)
        new_plan.metadata["strategy"] = self.name


        return new_plan

    def decompose_goal(self, goal: Goal) -> list[Task]:
        """
        Decompose a Goal into planning Tasks.

        The default strategy creates one Task for each success criterion.

        If the Goal has no success criteria, one fallback Task is created.

        This method creates cognitive planning objects only. It does not
        create execution nodes or invoke runtime components.
        """
        if not isinstance(goal, Goal):
            raise TypeError("goal must be an instance of Goal")

        tasks: list[Task] = []

        for criterion in goal.success_criteria:
            tasks.append(
                Task(
                    description=f"Achieve criterion: {criterion}",
                )
            )

        if not tasks:
            tasks.append(
                Task(
                    description=f"Plan execution for {goal.description}",
                )
            )

        return tasks

    def info(self) -> dict[str, str]:
        """
        Return immutable strategy metadata as a new dictionary.
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}"
            ")"
        )