"""
SciOS Cognitive Core Planner
============================

Canonical planning orchestrator for the Cognitive Core.

Contract:

    Goal -> Task decomposition -> Plan

The Planner constructs cognitive Plans only.

It does NOT:
    - execute tasks
    - schedule execution
    - invoke tools
    - monitor runtime state
    - retry execution
    - recover failed execution
    - create ExecutionGraph objects
"""

from __future__ import annotations

from collections.abc import Iterable

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

    Responsibility
    --------------
    Decompose a Goal into Tasks and construct a canonical Plan.

    Non-responsibility
    ------------------
    Runtime execution, scheduling, monitoring, retry, recovery,
    tool invocation, or execution-graph construction.
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

        if strategy is None:
            strategy = PlanningStrategy()

        self.strategy = strategy

    # ==========================================================
    # Planning
    # ==========================================================

    def create_plan(
        self,
        goal: Goal,
        tasks: Iterable[str | Task] | None = None,
    ) -> Plan:
        """
        Construct a canonical Plan for ``goal``.

        Parameters
        ----------
        goal:
            Cognitive planning Goal.

        tasks:
            Optional explicit task definitions.

            Each item may be:
                - ``str`` -> converted to ``Task(description=...)``
                - ``Task`` -> preserved

            When omitted, ``self.strategy`` decomposes the Goal.

        Returns
        -------
        Plan
            Canonical cognitive planning representation.

        Raises
        ------
        TypeError
            If ``goal`` is not a Goal or an explicit task has an
            unsupported type.

        Notes
        -----
        This method only constructs a Plan. It never executes it.
        """

        if not isinstance(goal, Goal):
            raise TypeError(
                "goal must be an instance of Goal"
            )

        normalized_tasks = self._normalize_tasks(
            tasks
        )

        if normalized_tasks is None:
            normalized_tasks = list(
                self.strategy.decompose_goal(goal)
            )

        return Plan(
            goal=goal,
            tasks=normalized_tasks,
        )

    # ==========================================================
    # Task normalization
    # ==========================================================

    @staticmethod
    def _normalize_tasks(
        tasks: Iterable[str | Task] | None,
    ) -> list[Task] | None:
        """
        Normalize explicit task definitions.

        ``None`` means that the configured PlanningStrategy should
        perform goal decomposition.
        """

        if tasks is None:
            return None

        normalized: list[Task] = []

        for item in tasks:
            if isinstance(item, Task):
                normalized.append(item)

            elif isinstance(item, str):
                normalized.append(
                    Task(
                        description=item
                    )
                )

            else:
                raise TypeError(
                    "tasks must contain only str or Task instances"
                )

        return normalized

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def reset(self) -> None:
        """
        Restore the default PlanningStrategy.

        Planner state does not contain Plans or runtime execution
        state. Reset only restores planner-local strategy
        configuration.
        """

        self.strategy = PlanningStrategy()

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"strategy={self.strategy.name!r}"
            ")"
        )