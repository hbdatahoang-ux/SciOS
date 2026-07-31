"""
SciOS Cognitive Core Goal
=========================

Goal model for planning and reasoning.

Responsibilities
-----------------
- Represent planning objectives.
- Maintain success criteria.
- Maintain constraints.
- Evaluate goal completion.

Design Goals
------------
- Python 3.11+
- Backward compatible API
- Planner-friendly
- Extensible evaluation model
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "Goal",
]


class Goal:
    """
    Goal represents a high-level objective.

    A Goal contains:

    - description
    - success criteria
    - constraints
    """


    def __init__(
        self,
        description: str,
        success_criteria: list[str] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> None:


        if not isinstance(
            description,
            str,
        ):
            raise TypeError(
                "description must be a string"
            )


        self.description = description


        self.success_criteria: list[str] = (
            list(success_criteria)
            if success_criteria
            else []
        )


        self.constraints: dict[str, Any] = (
            dict(constraints)
            if constraints
            else {}
        )



    # ======================================================
    # Criteria Management
    # ======================================================

    def add_success_criterion(
        self,
        criterion: str,
    ) -> None:
        """
        Add success criterion.
        """

        if not isinstance(
            criterion,
            str,
        ):
            raise TypeError(
                "criterion must be a string"
            )


        if criterion not in self.success_criteria:

            self.success_criteria.append(
                criterion
            )



    def add_constraint(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add goal constraint.
        """

        self.constraints[key] = value



    # ======================================================
    # Evaluation
    # ======================================================

    def is_successful(
        self,
        context: dict[str, Any],
    ) -> bool:
        """
        Evaluate goal completion.

        Rules
        -----
        - No criteria:
            Goal automatically succeeds.
        - With criteria:
            All criteria must evaluate True.

        Example
        -------
        context = {
            "released": True
        }
        """

        if not self.success_criteria:

            return True



        for criterion in self.success_criteria:

            if not context.get(
                criterion,
                False,
            ):
                return False


        return True



    def is_satisfied(
        self,
        results: dict[str, Any],
    ) -> bool:
        """
        Backward compatible evaluator.

        Supports old format:

        {
            "achievements": [
                "criterion A"
            ]
        }

        Also supports direct context:

        {
            "criterion A": True
        }
        """

        if not self.success_criteria:

            return True



        # New style context

        if all(
            isinstance(
                results.get(c),
                bool,
            )
            for c in self.success_criteria
            if c in results
        ):

            return self.is_successful(
                results
            )



        # Legacy achievements format

        achievements = results.get(
            "achievements",
            [],
        )


        return all(
            criterion in achievements
            for criterion in self.success_criteria
        )



    # ======================================================
    # Utilities
    # ======================================================

    def reset(self) -> None:
        """
        Reset goal state.

        Keeps definition but clears dynamic constraints.
        """

        self.constraints.clear()



    def to_dict(self) -> dict[str, Any]:
        """
        Serialize goal.
        """

        return {
            "description": self.description,
            "success_criteria": list(
                self.success_criteria
            ),
            "constraints": dict(
                self.constraints
            ),
        }



    # ======================================================
    # Protocols
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"Goal("
            f"description={self.description!r}, "
            f"criteria={len(self.success_criteria)}, "
            f"constraints={len(self.constraints)}"
            f")"
        )