"""
SciOS Cognitive Core - Planning Goal
====================================

High-level goal representation for cognitive planning.

A Goal defines:
    - a description,
    - success criteria,
    - planning constraints.

A Goal contains no execution lifecycle or runtime state.
"""

from __future__ import annotations

from typing import Any

__all__ = ["Goal"]


class Goal:
    """
    High-level objective used by the cognitive planner.

    Goal is a declarative planning object. It describes what should
    be achieved and how achievement can be evaluated.
    """

    def __init__(
        self,
        description: str,
        success_criteria: list[str] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(description, str):
            raise TypeError("description must be a string")

        if success_criteria is not None:
            if not isinstance(success_criteria, list):
                raise TypeError(
                    "success_criteria must be a list or None"
                )

            if not all(
                isinstance(criterion, str)
                for criterion in success_criteria
            ):
                raise TypeError(
                    "success_criteria must contain only strings"
                )

        if constraints is not None and not isinstance(constraints, dict):
            raise TypeError(
                "constraints must be a dict or None"
            )

        self.description = description

        self.success_criteria: list[str] = list(
            success_criteria
        ) if success_criteria is not None else []

        self.constraints: dict[str, Any] = (
            dict(constraints)
            if constraints is not None
            else {}
        )

    # ==========================================================
    # Criteria
    # ==========================================================

    def add_success_criterion(self, criterion: str) -> None:
        """Add a unique success criterion."""
        if not isinstance(criterion, str):
            raise TypeError("criterion must be a string")

        if criterion not in self.success_criteria:
            self.success_criteria.append(criterion)

    # ==========================================================
    # Constraints
    # ==========================================================

    def add_constraint(self, key: str, value: Any) -> None:
        """Add or replace a planning constraint."""
        if not isinstance(key, str):
            raise TypeError("key must be a string")

        self.constraints[key] = value

    # ==========================================================
    # Evaluation
    # ==========================================================

    def is_successful(self, context: dict[str, Any]) -> bool:
        """
        Evaluate the goal against a boolean success context.

        A goal without criteria is considered satisfied.
        When criteria exist, every criterion must evaluate to True.
        """
        if not isinstance(context, dict):
            raise TypeError("context must be a dict")

        if not self.success_criteria:
            return True

        return all(
            context.get(criterion, False) is True
            for criterion in self.success_criteria
        )

    def is_satisfied(self, results: dict[str, Any]) -> bool:
        """
        Backward-compatible goal evaluation.

        Supports both:

            {"criterion": True}

        and legacy:

            {"achievements": ["criterion"]}
        """
        if not isinstance(results, dict):
            raise TypeError("results must be a dict")

        if not self.success_criteria:
            return True

        direct_context = all(
            criterion in results
            and isinstance(results[criterion], bool)
            for criterion in self.success_criteria
        )

        if direct_context:
            return self.is_successful(results)

        achievements = results.get("achievements", [])

        if not isinstance(achievements, (list, tuple, set)):
            return False

        return all(
            criterion in achievements
            for criterion in self.success_criteria
        )

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the goal."""
        return {
            "description": self.description,
            "success_criteria": list(self.success_criteria),
            "constraints": dict(self.constraints),
        }

    # ==========================================================
    # Protocol
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"Goal("
            f"description={self.description!r}, "
            f"criteria={len(self.success_criteria)}, "
            f"constraints={len(self.constraints)}"
            f")"
        )