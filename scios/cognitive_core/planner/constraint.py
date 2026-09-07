"""
SciOS Cognitive Core - Planning Constraints
===========================================

Declarative constraints used by the cognitive planning layer.

Constraints describe conditions that a Goal, Objective, Task, or Plan
may need to satisfy.

This module contains planning-domain data only.

Non-responsibilities:
    - execution lifecycle
    - scheduling
    - runtime state
    - tool invocation
    - resource allocation
"""

from __future__ import annotations

from typing import Any

__all__ = ["Constraint", "ConstraintSet"]


class Constraint:
    """
    A single declarative planning constraint.

    A constraint consists of:
        - name: logical name of the constrained property
        - value: expected value
        - constraint_type: semantic category of the constraint

    The default satisfaction rule is exact key/value matching:

        context[constraint.name] == constraint.value

    More sophisticated constraint semantics can be introduced later
    without coupling this object to runtime execution.
    """

    def __init__(
        self,
        name: str,
        value: Any,
        constraint_type: str = "generic",
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not isinstance(constraint_type, str):
            raise TypeError("constraint_type must be a string")

        self.name = name
        self.value = value
        self.constraint_type = constraint_type

    def is_satisfied(self, context: dict[str, Any]) -> bool:
        """
        Check whether this constraint is satisfied by a context.

        The default semantic is exact equality between the expected
        constraint value and the corresponding context value.

        A missing key is therefore considered unsatisfied.
        """
        if not isinstance(context, dict):
            raise TypeError("context must be a dict")

        return (
            self.name in context
            and context[self.name] == self.value
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the constraint."""
        return {
            "name": self.name,
            "value": self.value,
            "constraint_type": self.constraint_type,
        }

    def __repr__(self) -> str:
        return (
            f"<Constraint "
            f"{self.name}={self.value!r} "
            f"type={self.constraint_type!r}>"
        )


class ConstraintSet:
    """
    Collection of named planning constraints.

    Constraints are keyed by their name. Adding a constraint with an
    existing name replaces the previous constraint.

    ConstraintSet is declarative and contains no runtime state.
    """

    def __init__(
        self,
        constraints: list[Constraint] | None = None,
    ) -> None:
        if constraints is not None:
            if not isinstance(constraints, list):
                raise TypeError(
                    "constraints must be a list or None"
                )

            if not all(
                isinstance(constraint, Constraint)
                for constraint in constraints
            ):
                raise TypeError(
                    "constraints must contain only Constraint instances"
                )

        self.constraints: dict[str, Constraint] = {}

        if constraints is not None:
            for constraint in constraints:
                self.add_constraint(constraint)

    def add_constraint(self, constraint: Constraint) -> None:
        """
        Add or replace a constraint.

        Constraint names are unique within a ConstraintSet.
        """
        if not isinstance(constraint, Constraint):
            raise TypeError(
                "constraint must be an instance of Constraint"
            )

        self.constraints[constraint.name] = constraint

    def get_constraint(self, name: str) -> Constraint | None:
        """Return a constraint by name, or None when absent."""
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        return self.constraints.get(name)

    def is_satisfied(self, context: dict[str, Any]) -> bool:
        """
        Check whether all constraints are satisfied.

        An empty ConstraintSet is considered satisfied.
        """
        if not isinstance(context, dict):
            raise TypeError("context must be a dict")

        return all(
            constraint.is_satisfied(context)
            for constraint in self.constraints.values()
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation of the constraint set."""
        return {
            name: constraint.to_dict()
            for name, constraint in self.constraints.items()
        }

    def __len__(self) -> int:
        return len(self.constraints)

    def __repr__(self) -> str:
        return f"<ConstraintSet size={len(self.constraints)}>"