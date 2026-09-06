"""
SciOS Cognitive Core Planning Strategy
======================================

Planning strategy abstraction for the SciOS planner.
"""

from __future__ import annotations

from .goal import Goal
from .objective import Objective
from .plan import Plan
from .task import Task


__all__ = [
    "PlanningStrategy",
]


class PlanningStrategy:
    """
    Default planning strategy.

    The strategy can be named and described, then applied to a Plan.
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

        self.name = name
        self.description = description

    def apply(
        self,
        plan: Plan,
    ) -> Plan:
        """
        Apply this strategy to a plan.

        The default strategy preserves the goal and tasks while
        recording the selected strategy in plan metadata.
        """

        if not isinstance(plan, Plan):
            raise TypeError(
                "plan must be an instance of Plan"
            )

        new_plan = Plan(
            goal=plan.goal,
            tasks=list(plan.tasks),
            constraints=plan.constraints,
        )

        new_plan.metadata = dict(
            plan.metadata
        )

        new_plan.metadata["strategy"] = self.name

        return new_plan

    def decompose_goal(
        self,
        goal: Goal,
    ) -> list[Task]:
        """
        Decompose a goal into planning tasks.

        Creates one task for each success criterion.
        If the goal has no criteria, creates one default task.
        """

        if not isinstance(goal, Goal):
            raise TypeError(
                "goal must be an instance of Goal"
            )

        objective = Objective(
            description=f"Subgoal of {goal.description}",
            parent_goal=goal.description,
        )

        tasks: list[Task] = []

        for criterion in goal.success_criteria:

            task = Task(
                description=f"Achieve criterion: {criterion}"
            )

            objective.add_task(task)
            tasks.append(task)

        if not tasks:

            task = Task(
                description=(
                    f"Plan execution for {goal.description}"
                )
            )

            objective.add_task(task)
            tasks.append(task)

        return tasks

    def info(self) -> dict[str, str]:
        """
        Return strategy metadata.
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
