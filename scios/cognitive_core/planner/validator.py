"""
SciOS Cognitive Core Plan Validator
====================================

Structural validation for the canonical cognitive planning model.

This module validates Goal, Task, TaskGraph, ConstraintSet, and Plan
structure. It does not execute tasks, schedule runtime work, or validate
runtime execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from .constraint import Constraint, ConstraintSet
from .goal import Goal
from .plan import Plan
from .task import Task
from .task_graph import TaskGraph

__all__ = [
    "VALID",
    "INVALID",
    "VALIDATOR_NAME",
    "VALIDATION_VERSION",
    "DEFAULT_MAX_ERRORS",
    "DEFAULT_MAX_WARNINGS",
    "ValidationIssue",
    "ValidationReport",
    "PlanValidator",
]


VALID: Final[bool] = True
INVALID: Final[bool] = False

VALIDATOR_NAME: Final[str] = "PlanValidator"
VALIDATION_VERSION: Final[str] = "1.0.0"

DEFAULT_MAX_ERRORS: Final[int] = 1024
DEFAULT_MAX_WARNINGS: Final[int] = 1024

SEVERITY_ERROR: Final[str] = "error"
SEVERITY_WARNING: Final[str] = "warning"

ERRORS_KEY: Final[str] = "errors"
WARNINGS_KEY: Final[str] = "warnings"
VALID_KEY: Final[str] = "valid"
METADATA_KEY: Final[str] = "metadata"


@dataclass(slots=True)
class ValidationIssue:
    """Represents one validation issue."""

    code: str
    message: str
    severity: str = SEVERITY_ERROR
    location: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return self.severity == SEVERITY_ERROR

    @property
    def is_warning(self) -> bool:
        return self.severity == SEVERITY_WARNING

    def to_dict(self) -> dict[str, Any]:
        """Serialize this issue without exposing mutable internal state."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class ValidationReport:
    """Mutable report container for one validation run."""

    valid: bool = VALID
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    @property
    def issue_count(self) -> int:
        return self.error_count + self.warning_count

    @property
    def issues(self) -> list[ValidationIssue]:
        return [*self.errors, *self.warnings]

    def clear(self) -> None:
        self.valid = VALID
        self.errors.clear()
        self.warnings.clear()
        self.metadata.clear()

    def add_error(
        self,
        code: str,
        message: str,
        *,
        location: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.valid = INVALID
        self.errors.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=SEVERITY_ERROR,
                location=location,
                metadata=dict(metadata or {}),
            )
        )

    def add_warning(
        self,
        code: str,
        message: str,
        *,
        location: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.warnings.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=SEVERITY_WARNING,
                location=location,
                metadata=dict(metadata or {}),
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            VALID_KEY: self.valid,
            ERRORS_KEY: [issue.to_dict() for issue in self.errors],
            WARNINGS_KEY: [issue.to_dict() for issue in self.warnings],
            METADATA_KEY: {
                **self.metadata,
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "issue_count": self.issue_count,
            },
        }


class PlanValidator:
    """
    Validate the structure of a cognitive Plan.

    Validation is intentionally separate from execution. A valid Plan
    is structurally coherent; it is not necessarily executable.
    """

    def __init__(
        self,
        *,
        strict: bool = False,
        max_errors: int = DEFAULT_MAX_ERRORS,
        max_warnings: int = DEFAULT_MAX_WARNINGS,
    ) -> None:
        self._strict = bool(strict)
        self._max_errors = self._normalize_limit(
            max_errors,
            "max_errors",
        )
        self._max_warnings = self._normalize_limit(
            max_warnings,
            "max_warnings",
        )

        self._report = ValidationReport()
        self._statistics: dict[str, int] = {
            "validation_count": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "error_count": 0,
            "warning_count": 0,
        }

    @staticmethod
    def _normalize_limit(value: int, name: str) -> int:
        if isinstance(value, bool):
            raise TypeError(f"{name} must be an integer")

        try:
            normalized = int(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{name} must be an integer") from exc

        return max(0, normalized)

    def validate(self, plan: Plan) -> dict[str, Any]:
        """
        Validate an entire Plan.

        Returns a compatibility dictionary containing validity and
        human-readable error/warning messages.
        """
        self._report = ValidationReport()
        self._statistics["validation_count"] += 1

        if plan is None:
            self._error("PLAN_NULL", "Plan is None.")
        elif not isinstance(plan, Plan):
            self._error(
                "PLAN_INVALID",
                "Plan must be an instance of Plan.",
            )
        else:
            self.validate_goal(plan)
            self.validate_tasks(plan)
            self.validate_constraints(plan)
            self.validate_graph(plan)
            self.validate_metadata(plan)

        if self._report.valid:
            self._statistics["valid_count"] += 1
        else:
            self._statistics["invalid_count"] += 1

        self._statistics["error_count"] += self._report.error_count
        self._statistics["warning_count"] += self._report.warning_count

        return self._compatibility_result()

    def _compatibility_result(self) -> dict[str, Any]:
        return {
            VALID_KEY: self._report.valid,
            ERRORS_KEY: [
                issue.message
                for issue in self._report.errors
            ],
            WARNINGS_KEY: [
                issue.message
                for issue in self._report.warnings
            ],
            "issues": [
                issue.to_dict()
                for issue in self._report.issues
            ],
        }

    def validate_goal(self, plan: Plan) -> None:
        """Validate Goal structure."""
        goal = getattr(plan, "goal", None)

        if not isinstance(goal, Goal):
            self._error(
                "GOAL_INVALID",
                "Plan goal must be an instance of Goal.",
                location="goal",
            )
            return

        if not isinstance(goal.description, str):
            self._error(
                "GOAL_DESCRIPTION_INVALID",
                "Goal description must be a string.",
                location="goal.description",
            )
        elif not goal.description.strip():
            self._error(
                "GOAL_EMPTY",
                "Goal description is empty.",
                location="goal.description",
            )

        if not isinstance(goal.success_criteria, list):
            self._error(
                "GOAL_CRITERIA_INVALID",
                "Goal success_criteria must be a list.",
                location="goal.success_criteria",
            )
            return

        for index, criterion in enumerate(goal.success_criteria):
            if not isinstance(criterion, str):
                self._error(
                    "GOAL_CRITERION_INVALID",
                    "Goal success criteria must contain only strings.",
                    location=f"goal.success_criteria[{index}]",
                )
            elif not criterion.strip():
                self._error(
                    "GOAL_CRITERION_EMPTY",
                    "Goal success criterion is empty.",
                    location=f"goal.success_criteria[{index}]",
                )

    def validate_tasks(self, plan: Plan) -> None:
        """Validate Task structure without checking execution state."""
        tasks = getattr(plan, "tasks", None)

        if not isinstance(tasks, list):
            self._error(
                "TASKS_INVALID",
                "Plan tasks must be a list.",
                location="tasks",
            )
            return

        if not tasks:
            self._error(
                "TASKS_EMPTY",
                "No tasks.",
                location="tasks",
            )
            return

        seen_ids: set[str] = set()

        for index, task in enumerate(tasks):
            location = f"tasks[{index}]"

            if not isinstance(task, Task):
                self._error(
                    "TASK_INVALID",
                    "Plan tasks must contain only Task instances.",
                    location=location,
                )
                continue

            if not isinstance(task.description, str):
                self._error(
                    "TASK_DESCRIPTION_INVALID",
                    "Task description must be a string.",
                    location=f"{location}.description",
                )
            elif not task.description.strip():
                self._error(
                    "TASK_DESCRIPTION_EMPTY",
                    "Task description is empty.",
                    location=f"{location}.description",
                )

            task_id = task.id

            if task_id is not None:
                if not isinstance(task_id, str):
                    self._error(
                        "TASK_ID_INVALID",
                        "Task ID must be a string or None.",
                        location=f"{location}.id",
                    )
                elif task_id in seen_ids:
                    self._error(
                        "TASK_ID_DUPLICATE",
                        f"Duplicate task ID: {task_id!r}.",
                        location=f"{location}.id",
                    )
                else:
                    seen_ids.add(task_id)

            dependencies = task.dependencies

            if not isinstance(dependencies, list):
                self._error(
                    "TASK_DEPENDENCIES_INVALID",
                    "Task dependencies must be a list.",
                    location=f"{location}.dependencies",
                )
                continue

            for dependency in dependencies:
                if not isinstance(dependency, str):
                    self._error(
                        "TASK_DEPENDENCY_ID_INVALID",
                        "Task dependency IDs must be strings.",
                        location=f"{location}.dependencies",
                    )
                elif task_id is not None and dependency == task_id:
                    self._error(
                        "TASK_SELF_DEPENDENCY",
                        f"Task {task_id!r} cannot depend on itself.",
                        location=f"{location}.dependencies",
                    )

    def validate_constraints(self, plan: Plan) -> None:
        """
        Validate ConstraintSet structure.

        This method does not evaluate constraint satisfaction against
        runtime context or Plan metadata.
        """
        constraints = getattr(plan, "constraints", None)

        if constraints is None:
            self._warning(
                "CONSTRAINTS_MISSING",
                "Plan constraints are missing.",
                location="constraints",
            )
            return

        if not isinstance(constraints, ConstraintSet):
            self._error(
                "CONSTRAINTS_INVALID",
                "Plan constraints must be a ConstraintSet.",
                location="constraints",
            )
            return

        raw_constraints = getattr(constraints, "_constraints", None)

        if raw_constraints is None:
            return

        if not isinstance(raw_constraints, dict):
            self._error(
                "CONSTRAINTS_STORAGE_INVALID",
                "ConstraintSet internal storage must be a dictionary.",
                location="constraints",
            )
            return

        for name, constraint in raw_constraints.items():
            location = f"constraints[{name!r}]"

            if not isinstance(name, str):
                self._error(
                    "CONSTRAINT_NAME_INVALID",
                    "Constraint names must be strings.",
                    location=location,
                )

            if not isinstance(constraint, Constraint):
                self._error(
                    "CONSTRAINT_INVALID",
                    "ConstraintSet must contain Constraint instances.",
                    location=location,
                )

    def validate_graph(self, plan: Plan) -> None:
        valid_tasks = [
            task for task in plan.tasks
            if isinstance(task, Task)
        ]

        task_ids = {
            task.id
            for task in valid_tasks
            if task.id is not None
        }

        # Kiểm tra mọi task đều có ID hợp lệ
        for task in valid_tasks:
            if task.id is None:
                self._error(
                    code="TASK_ID_MISSING",
                    message="Task must have an ID.",
                    location="tasks",
                )
                continue

            # Kiểm tra dependency tồn tại
            for dependency_id in task.dependencies:
                if dependency_id not in task_ids:
                    self._error(
                        code="DEPENDENCY_MISSING",
                        message=(
                            f"Task '{task.id}' depends on "
                            f"unknown task '{dependency_id}'."
                        ),
                        location=f"tasks.{task.id}.dependencies",
                        metadata={
                            "task_id": task.id,
                            "dependency_id": dependency_id,
                        },
                    )

                if dependency_id == task.id:
                    self._error(
                        code="SELF_DEPENDENCY",
                        message=f"Task '{task.id}' cannot depend on itself.",
                        location=f"tasks.{task.id}.dependencies",
                        metadata={"task_id": task.id},
                    )

        # Kiểm tra graph storage nếu graph có tồn tại
        graph = plan.task_graph
        if graph is None:
            self._error(
                code="TASK_GRAPH_MISSING",
                message="Plan task graph is missing.",
                location="task_graph",
            )
            return

        graph_task_ids = set(graph.tasks.keys())

        if graph_task_ids != task_ids:
            self._error(
                code="GRAPH_TASK_MISMATCH",
                message="TaskGraph task IDs do not match Plan task IDs.",
                location="task_graph.tasks",
                metadata={
                    "plan_task_ids": sorted(task_ids),
                    "graph_task_ids": sorted(graph_task_ids),
                },
            )

        self._validate_cycles(valid_tasks)

    def validate_metadata(self, plan: Plan) -> None:
        """Validate Plan metadata."""
        metadata = getattr(plan, "metadata", None)

        if metadata is None:
            self._warning(
                "METADATA_MISSING",
                "Metadata is missing.",
                location="metadata",
            )
            return

        if not isinstance(metadata, dict):
            self._error(
                "METADATA_INVALID",
                "Plan metadata must be a dictionary.",
                location="metadata",
            )

    def _error(
        self,
        code: str,
        message: str,
        *,
        location: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if self._report.error_count >= self._max_errors:
            return

        self._report.add_error(
            code,
            message,
            location=location,
            metadata=metadata,
        )

    def _warning(
        self,
        code: str,
        message: str,
        *,
        location: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if self._report.warning_count >= self._max_warnings:
            return

        self._report.add_warning(
            code,
            message,
            location=location,
            metadata=metadata,
        )

    def reset_statistics(self) -> "PlanValidator":
        """Reset accumulated validation statistics and current report."""
        self._report = ValidationReport()
        self._statistics = {
            "validation_count": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "error_count": 0,
            "warning_count": 0,
        }
        return self

    def statistics(self) -> dict[str, Any]:
        """Return accumulated validator statistics."""
        return dict(self._statistics)

    def diagnostics(self) -> dict[str, Any]:
        """Return validator identity, statistics, and latest report."""
        return {
            "validator": VALIDATOR_NAME,
            "version": VALIDATION_VERSION,
            "strict": self._strict,
            "statistics": self.statistics(),
            "report": self._report.to_dict(),
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"strict={self._strict}, "
            f"errors={self._report.error_count}, "
            f"warnings={self._report.warning_count})"
        )

    def __str__(self) -> str:
        return (
            f"{VALIDATOR_NAME}("
            f"valid={self._report.valid}, "
            f"errors={self._report.error_count}, "
            f"warnings={self._report.warning_count})"
        )

    def _validate_cycles(self, tasks: list[Task]) -> None:
        adjacency = {
            task.id: list(task.dependencies)
            for task in tasks
            if task.id is not None
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str, path: list[str]) -> None:
            if task_id in visiting:
                cycle_start = path.index(task_id)
                cycle = path[cycle_start:] + [task_id]

                self._error(
                    code="CYCLE_DETECTED",
                    message=(
                        "Task dependency cycle detected: "
                        + " -> ".join(cycle)
                    ),
                    location="tasks",
                    metadata={"cycle": cycle},
                )
                return

            if task_id in visited:
                return

            visiting.add(task_id)

            for dependency_id in adjacency.get(task_id, []):
                if dependency_id in adjacency:
                    visit(
                        dependency_id,
                        path + [dependency_id],
                    )

            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in adjacency:
            if task_id not in visited:
                visit(task_id, [task_id])
