# ==============================================================================
# Part 1
# Foundation
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from .constraint import ConstraintSet
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


# ==============================================================================
# Part 2
# Constants
# ==============================================================================

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


# ==============================================================================
# Part 3
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class ValidationIssue:
    """
    Represents a single validation issue.
    """

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
        return {
            "valid": self.valid,
            "errors": [
                issue.message
                for issue in self.errors
            ],
            "warnings": [
                issue.message
                for issue in self.warnings
            ],
        }


@dataclass(slots=True)
class ValidationReport:
    """
    Immutable validation result container.
    """

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
                metadata=metadata or {},
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
                metadata=metadata or {},
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            VALID_KEY: self.valid,
            ERRORS_KEY: [
                issue.message
                for issue in self.errors
            ],
            WARNINGS_KEY: [
                issue.message
                for issue in self.warnings
            ],
            METADATA_KEY: {
                **self.metadata,
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "issue_count": self.issue_count,
            },
        }

# ==============================================================================
# Part 4
# PlanValidator
# ==============================================================================


class PlanValidator:
    """
    Validate planner output.
    """


    def __init__(
        self,
        *,
        strict: bool = False,
        max_errors: int = DEFAULT_MAX_ERRORS,
        max_warnings: int = DEFAULT_MAX_WARNINGS,
    ) -> None:

        self._strict: bool = bool(strict)

        self._max_errors: int = max(
            0,
            int(max_errors),
        )

        self._max_warnings: int = max(
            0,
            int(max_warnings),
        )

        # ------------------------------------------------------------------
        # Runtime report
        # ------------------------------------------------------------------

        self._report: ValidationReport = (
            ValidationReport()
        )


        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._statistics: dict[str, int] = {

            "validation_count": 0,

            "valid_count": 0,

            "invalid_count": 0,

            "error_count": 0,

            "warning_count": 0,
        }

# ==============================================================================
# Part 5
# Validation API
# ==============================================================================

    def validate(
        self,
        plan: Plan,
    ) -> dict[str, Any]:
        """
        Validate an entire plan.
        Returns a dictionary for compatibility with existing tests.
        """

        self._report = ValidationReport()

        self._statistics["validation_count"] += 1

        if plan is None:

            self._report.add_error(
                "PLAN_NULL",
                "Plan is None.",
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

        self._statistics["error_count"] += (
            self._report.error_count
        )

        self._statistics["warning_count"] += (
            self._report.warning_count
        )

        return {
            "valid": self._report.valid,
            "errors": [
                issue.message
                for issue in self._report.errors
            ],
            "warnings": [
                issue.message
                for issue in self._report.warnings
            ],
        }


    def validate_goal(
        self,
        plan: Plan,
    ) -> None:
        """
        Validate goal.
        """

        goal = getattr(
            plan,
            "goal",
            None,
        )

        if goal is None:

            self._report.add_error(
                "GOAL_MISSING",
                "Missing goal.",
            )

            return

        description = getattr(
            goal,
            "description",
            "",
        )

        if not str(description).strip():

            self._report.add_error(
                "GOAL_EMPTY",
                "Goal description is empty.",
            )


    def validate_tasks(
        self,
        plan: Plan,
    ) -> None:
        """
        Validate task structure.

        Planning validation is structural only. Task execution
        lifecycle state is intentionally outside the Planner contract.
        """

        tasks = list(
            getattr(
                plan,
                "tasks",
                [],
            )
            or []
        )

        if not tasks:

            self._report.add_error(
                "TASKS_EMPTY",
                "No tasks.",
            )

            return

        for task in tasks:

            description = getattr(
                task,
                "description",
                "",
            )

            if not str(description).strip():

                self._report.add_error(
                    "TASK_DESCRIPTION_EMPTY",
                    "Task description is empty.",
                )

            dependencies = getattr(
                task,
                "dependencies",
                [],
            )

            if dependencies is None:
                continue

            if not isinstance(
                dependencies,
                (list, tuple, set),
            ):

                self._report.add_error(
                    "TASK_DEPENDENCIES_INVALID",
                    description or "Unnamed task",
                )

    def validate_constraints(
        self,
        plan: Plan,
    ) -> None:
        """
        Validate constraints.
        """

        constraints = getattr(
            plan,
            "constraints",
            None,
        )

        if constraints is None:
            return

        if hasattr(
            constraints,
            "is_satisfied",
        ):

            try:

                metadata = getattr(
                    plan,
                    "metadata",
                    {},
                )

                if not constraints.is_satisfied(
                    metadata
                ):

                    self._report.add_error(
                        "CONSTRAINT_FAILED",
                        "Constraint validation failed.",
                    )

            except Exception as exc:

                self._report.add_error(
                    "CONSTRAINT_EXCEPTION",
                    str(exc),
                )


    def validate_graph(
        self,
        plan: Plan,
    ) -> None:
        """
        Validate task graph.
        """

        graph = getattr(
            plan,
            "task_graph",
            None,
        )

        if graph is None:
            return

        if hasattr(
            graph,
            "topological_sort",
        ):

            try:

                graph.topological_sort()

            except Exception as exc:

                self._report.add_error(
                    "GRAPH_INVALID",
                    str(exc),
                )


    def validate_metadata(
        self,
        plan: Plan,
    ) -> None:
        """
        Validate metadata.
        """

        metadata = getattr(
            plan,
            "metadata",
            None,
        )

        if metadata is None:

            self._report.add_warning(
                "METADATA_MISSING",
                "Metadata is missing.",
            )

            return

        if not isinstance(
            metadata,
            dict,
        ):

            self._report.add_warning(
                "METADATA_INVALID",
                "Metadata should be a dictionary.",
            )

# ==============================================================================
# Part 6
# Helpers
# ==============================================================================

    def _error(
        self,
        code: str,
        message: str,
        *,
        location: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register validation error.
        """

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
        """
        Register validation warning.
        """

        if self._report.warning_count >= self._max_warnings:
            return

        self._report.add_warning(
            code,
            message,
            location=location,
            metadata=metadata,
        )


# ==============================================================================
# Part 7
# Statistics
# ==============================================================================

    def reset_statistics(
        self,
    ) -> "PlanValidator":
        """
        Reset runtime statistics.
        """

        self._report = ValidationReport()

        return self


    def statistics(
        self,
    ) -> dict[str, Any]:
        """
        Return validator statistics.
        """

        return {
            "valid": self._report.valid,
            "errors": self._report.error_count,
            "warnings": self._report.warning_count,
            "issues": (
                self._report.error_count
                + self._report.warning_count
            ),
        }


    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return diagnostics.
        """

        return {
            "validator": VALIDATOR_NAME,
            "version": VALIDATION_VERSION,
            "strict": self._strict,
            "statistics": self.statistics(),
            "report": self._report.to_dict(),
        }


# ==============================================================================
# Part 8
# Protocols
# ==============================================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"strict={self._strict}, "
            f"errors={self._report.error_count}, "
            f"warnings={self._report.warning_count})"
        )


    def __str__(
        self,
    ) -> str:

        return (
            f"{VALIDATOR_NAME}"
            f"(valid={self._report.valid}, "
            f"errors={self._report.error_count}, "
            f"warnings={self._report.warning_count})"
        )
