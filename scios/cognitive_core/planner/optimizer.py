"""
SciOS Plan Optimizer
====================

Plan optimization engine.

Responsibilities
----------------
- Optimize execution plans.
- Preserve goal integrity.
- Preserve tasks.
- Attach optimization metadata.

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from .plan import Plan


__all__ = [
    "PlanOptimizer",
]



class PlanOptimizer:
    """
    Planner optimization component.

    Example
    -------

    optimizer = PlanOptimizer(
        name="BasicOptimizer"
    )

    new_plan = optimizer.optimize(plan)
    """



    def __init__(
        self,
        name: str = "DefaultOptimizer",
    ) -> None:

        self.name = name

        self._history: list[Plan] = []



    # ======================================================
    # Optimization
    # ======================================================

    def optimize(
        self,
        plan: Plan,
    ) -> Plan:
        """
        Optimize a plan.

        Guarantees
        ----------
        - Same goal.
        - Same tasks.
        - Metadata updated.
        """

        if not isinstance(
            plan,
            Plan,
        ):
            raise TypeError(
                "optimize() requires Plan instance"
            )


        # Preserve existing metadata

        if not hasattr(
            plan,
            "metadata",
        ) or plan.metadata is None:

            plan.metadata = {}



        plan.metadata[
            "optimized_by"
        ] = self.name



        self._history.append(
            plan
        )


        return plan



    # ======================================================
    # Diagnostics
    # ======================================================

    @property
    def history(
        self,
    ) -> list[Plan]:

        return list(
            self._history
        )



    def reset(
        self,
    ) -> None:

        self._history.clear()



    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "name": self.name,

            "optimized_plans":
                len(self._history),

        }



    # ======================================================
    # Protocols
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"name={self.name!r}, "

            f"history={len(self._history)}"

            ")"

        )