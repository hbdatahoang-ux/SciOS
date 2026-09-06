"""
SciOS Cognitive Core Planner
============================

Canonical planning orchestrator for the Cognitive Core.

The Planner constructs Plans.
It does not execute them.
"""

from __future__ import annotations

from typing import Iterable

from .goal import Goal
from .plan import Plan
from .strategy import PlanningStrategy
from .task import Task


__all__ = [
    "Planner",
]


class Planner:
    """
    Canonical Cognitive Core Planner.

    Responsibility:
        Goal -> Task decomposition -> Plan construction

    Non-responsibility:
        Plan execution, monitoring, retry, recovery, or runtime
        tool invocation.
    """

    def __init__(
        self,
        strategy: PlanningStrategy | None = None,
    ) -> None:
        if strategy is not None and not isinstance(
            strategy,
            PlanningStrategy,
        ):
            raise TypeError(
                "strategy must be an instance of PlanningStrategy"
            )

        self.strategy = strategy or PlanningStrategy()

    def create_plan(
        self,
        goal: Goal,
        tasks: Iterable[str | Task] | None = None,
    ) -> Plan:
        """
        Construct a Plan for the supplied Goal.

        If explicit tasks are supplied, they are normalized and used
        directly.

        If no tasks are supplied, the configured PlanningStrategy
        decomposes the Goal into tasks.

        This method only constructs a plan. It never executes tasks.
        """

        if not isinstance(goal, Goal):
            raise TypeError(
                "goal must be an instance of Goal"
            )

        if tasks is None:
            normalized = self.strategy.decompose_goal(goal)
        else:
            normalized: list[Task] = []

            for item in tasks:
                if isinstance(item, Task):
                    normalized.append(item)
                elif isinstance(item, str):
                    normalized.append(
                        Task(description=item)
                    )
                else:
                    raise TypeError(
                        "tasks must contain only str or Task instances"
                    )

        return Plan(
            goal=goal,
            tasks=normalized,
        )

    def reset(self) -> None:
        """
        Reset planner-local configuration.

        The canonical Planner is intentionally stateless with respect
        to plans and execution. Reset therefore only restores the
        default strategy when a custom strategy was supplied.
        """

        self.strategy = PlanningStrategy()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"strategy={self.strategy.name!r}"
            ")"
        )
