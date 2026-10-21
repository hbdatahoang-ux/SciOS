from __future__ import annotations

from typing import Any

from .constraint import Constraint, ConstraintSet
from .goal import Goal
from .plan import Plan
from .task import Task

__all__ = ["PlanSerializer"]


class PlanSerializer:
    """Serialize and deserialize the canonical cognitive Plan."""

    @staticmethod
    def to_dict(plan: Plan) -> dict[str, Any]:
        if not isinstance(plan, Plan):
            raise TypeError("plan must be an instance of Plan")

        return plan.to_dict()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Plan:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        goal_data = data.get("goal")
        if not isinstance(goal_data, dict):
            raise ValueError("data['goal'] must be a dictionary")

        goal = Goal(
            description=goal_data.get("description", ""),
            success_criteria=goal_data.get("success_criteria", []),
            constraints=goal_data.get("constraints", {}),
        )

        task_data = data.get("tasks", [])
        if not isinstance(task_data, list):
            raise ValueError("data['tasks'] must be a list")

        tasks = [Task.from_dict(item) for item in task_data]

        constraints_data = data.get("constraints", {})
        if not isinstance(constraints_data, dict):
            raise ValueError("data['constraints'] must be a dictionary")

        constraint_set = ConstraintSet()

        for name, value in constraints_data.items():
            if not isinstance(value, dict):
                raise ValueError(
                    f"constraint '{name}' must be a dictionary"
                )

            constraint_set.add_constraint(
                Constraint(
                    name=value.get("name", name),
                    value=value.get("value"),
                    constraint_type=value.get(
                        "constraint_type",
                        "generic",
                    ),
                )
            )

        plan = Plan(
            goal=goal,
            constraints=constraint_set,
        )

        # TaskGraph requires dependencies to already exist.
        remaining = list(tasks)

        while remaining:
            progress = False

            for task in remaining[:]:
                if all(
                    plan.has_task(dependency)
                    for dependency in task.dependencies
                ):
                    plan.add_task(task)
                    remaining.remove(task)
                    progress = True

            if not progress:
                raise ValueError(
                    "Cannot reconstruct Plan: "
                    "missing dependency or dependency cycle."
                )

        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("data['metadata'] must be a dictionary")

        plan.metadata = dict(metadata)

        return plan

    @staticmethod
    def to_json(
        plan: Plan,
        *,
        indent: int = 2,
        sort_keys: bool = False,
    ) -> str:
        import json

        return json.dumps(
            PlanSerializer.to_dict(plan),
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=False,
        )

    @staticmethod
    def from_json(text: str) -> Plan:
        import json

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        return PlanSerializer.from_dict(json.loads(text))