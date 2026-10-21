"""
Contract tests for SciOS Cognitive Core PlanValidator.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.planner.constraint import (
    Constraint,
    ConstraintSet,
)
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.validator import (
    INVALID,
    VALID,
    PlanValidator,
    ValidationIssue,
    ValidationReport,
)


def make_valid_plan() -> Plan:
    goal = Goal(
        description="Improve system",
        success_criteria=["Increase reliability"],
    )

    task = Task(
        description="Analyze reliability",
        task_id="task-a",
    )

    return Plan(
        goal=goal,
        tasks=[task],
    )


class TestValidationIssue:
    def test_defaults(self):
        issue = ValidationIssue(
            code="TEST",
            message="Test issue",
        )

        assert issue.code == "TEST"
        assert issue.message == "Test issue"
        assert issue.severity == "error"
        assert issue.location == ""
        assert issue.is_error is True
        assert issue.is_warning is False

    def test_warning(self):
        issue = ValidationIssue(
            code="TEST_WARNING",
            message="Warning",
            severity="warning",
        )

        assert issue.is_error is False
        assert issue.is_warning is True

    def test_to_dict(self):
        issue = ValidationIssue(
            code="TEST",
            message="Invalid task",
            severity="error",
            location="tasks[0]",
            metadata={"index": 0},
        )

        assert issue.to_dict() == {
            "code": "TEST",
            "message": "Invalid task",
            "severity": "error",
            "location": "tasks[0]",
            "metadata": {"index": 0},
        }


class TestValidationReport:
    def test_default_report_is_valid(self):
        report = ValidationReport()

        assert report.valid is VALID
        assert report.error_count == 0
        assert report.warning_count == 0
        assert report.issue_count == 0
        assert report.issues == []

    def test_add_error_invalidates_report(self):
        report = ValidationReport()

        report.add_error("TEST", "Invalid")

        assert report.valid is INVALID
        assert report.error_count == 1
        assert report.warning_count == 0

    def test_add_warning_does_not_invalidate_report(self):
        report = ValidationReport()

        report.add_warning("TEST", "Warning")

        assert report.valid is VALID
        assert report.warning_count == 1

    def test_to_dict(self):
        report = ValidationReport()
        report.add_error("E001", "Error")
        report.add_warning("W001", "Warning")

        result = report.to_dict()

        assert result["valid"] is False
        assert result["errors"][0]["code"] == "E001"
        assert result["warnings"][0]["code"] == "W001"
        assert result["metadata"]["error_count"] == 1
        assert result["metadata"]["warning_count"] == 1
        assert result["metadata"]["issue_count"] == 2

    def test_clear(self):
        report = ValidationReport()
        report.add_error("E001", "Error")
        report.metadata["source"] = "test"

        report.clear()

        assert report.valid is True
        assert report.errors == []
        assert report.warnings == []
        assert report.metadata == {}


class TestPlanValidatorConstruction:
    def test_defaults(self):
        validator = PlanValidator()

        assert validator._strict is False
        assert validator._max_errors == 1024
        assert validator._max_warnings == 1024

    def test_strict_is_boolean(self):
        assert PlanValidator(strict=1)._strict is True
        assert PlanValidator(strict=0)._strict is False

    def test_limits_are_non_negative(self):
        validator = PlanValidator(
            max_errors=-1,
            max_warnings=-2,
        )

        assert validator._max_errors == 0
        assert validator._max_warnings == 0

    def test_limits_reject_booleans(self):
        with pytest.raises(TypeError):
            PlanValidator(max_errors=True)

    def test_limits_reject_invalid_values(self):
        with pytest.raises(TypeError):
            PlanValidator(max_errors="invalid")


class TestPlanValidatorValidate:
    def test_valid_plan(self):
        validator = PlanValidator()

        result = validator.validate(make_valid_plan())

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_none_plan(self):
        validator = PlanValidator()

        result = validator.validate(None)

        assert result["valid"] is False
        assert any("None" in error for error in result["errors"])

    def test_non_plan_input(self):
        validator = PlanValidator()

        result = validator.validate("invalid")

        assert result["valid"] is False

    def test_validation_increments_statistics(self):
        validator = PlanValidator()

        validator.validate(make_valid_plan())
        validator.validate(make_valid_plan())

        statistics = validator.statistics()

        assert statistics["validation_count"] == 2
        assert statistics["valid_count"] == 2
        assert statistics["invalid_count"] == 0

    def test_invalid_plan_increments_invalid_count(self):
        validator = PlanValidator()

        validator.validate(None)

        statistics = validator.statistics()

        assert statistics["validation_count"] == 1
        assert statistics["valid_count"] == 0
        assert statistics["invalid_count"] == 1
        assert statistics["error_count"] == 1

    def test_repeated_validation_resets_current_report(self):
        validator = PlanValidator()

        validator.validate(None)
        result = validator.validate(make_valid_plan())

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validation_is_structural_only(self):
        validator = PlanValidator()
        plan = make_valid_plan()

        plan.metadata["priority"] = "low"

        result = validator.validate(plan)

        assert result["valid"] is True


class TestPlanValidatorGoal:
    def test_missing_goal(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.goal = None

        result = validator.validate(plan)

        assert result["valid"] is False
        assert any("goal" in error.lower() for error in result["errors"])

    def test_empty_goal_description(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.goal.description = " "

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_invalid_success_criterion(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.goal.success_criteria.append(123)

        result = validator.validate(plan)

        assert result["valid"] is False


class TestPlanValidatorTasks:
    def test_empty_tasks(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.tasks = []

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_empty_task_description(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.tasks[0].description = " "

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_invalid_task_item(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.tasks = ["invalid"]

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_duplicate_task_ids(self):
        validator = PlanValidator()

        plan = make_valid_plan()
        plan.tasks.append(
            Task("Second", task_id="task-a")
        )

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_invalid_dependency_type(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.tasks[0].dependencies = [123]

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_self_dependency(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.tasks[0].dependencies = ["task-a"]

        result = validator.validate(plan)

        assert result["valid"] is False


class TestPlanValidatorConstraints:
    def test_valid_constraint_set(self):
        validator = PlanValidator()
        plan = make_valid_plan()

        plan.constraints = ConstraintSet(
            [
                Constraint(
                    name="priority",
                    value=5,
                )
            ]
        )

        result = validator.validate(plan)

        assert result["valid"] is True

    def test_missing_constraints_is_warning(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.constraints = None

        result = validator.validate(plan)

        assert result["valid"] is True
        assert result["warnings"]

    def test_invalid_constraints_type(self):
        validator = PlanValidator()
        plan = make_valid_plan()
        plan.constraints = "invalid"

        result = validator.validate(plan)

        assert result["valid"] is False


class TestPlanValidatorGraph:
    def test_valid_graph(self):
        validator = PlanValidator()

        result = validator.validate(make_valid_plan())

        assert result["valid"] is True

    def test_missing_dependency(self):
        validator = PlanValidator()
        plan = make_valid_plan()

        plan.tasks[0].dependencies = ["missing"]

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_cycle_is_invalid(self):
        validator = PlanValidator()

        task_a = Task(
            "A",
            task_id="a",
        )
        task_b = Task(
            "B",
            task_id="b",
        )

        plan = Plan(
            goal=Goal("Test"),
            tasks=[task_a, task_b],
        )

        task_a.dependencies = ["b"]
        task_b.dependencies = ["a"]

        result = validator.validate(plan)

        assert result["valid"] is False
        assert any(
            issue["code"] == "CYCLE_DETECTED"
            for issue in result["issues"]
        )

    def test_plan_graph_task_identity_mismatch(self):
        validator = PlanValidator()
        plan = make_valid_plan()

        original_task = plan.tasks[0]
        replacement_task = Task(
            description=original_task.description,
            task_id=original_task.id,
        )

        plan.task_graph.tasks[original_task.id] = replacement_task

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_task_dependencies_graph_edges_mismatch(self):
        validator = PlanValidator()

        task_a = Task(
            "A",
            task_id="task-a",
        )
        task_b = Task(
            "B",
            task_id="task-b",
        )

        plan = Plan(
            goal=Goal("Test"),
            tasks=[task_a, task_b],
        )

        task_b.dependencies = ["task-a"]
        plan.task_graph.edges["task-b"] = []

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_graph_edges_task_dependencies_mismatch(self):
        validator = PlanValidator()

        task_a = Task(
            "A",
            task_id="task-a",
        )
        task_b = Task(
            "B",
            task_id="task-b",
        )

        plan = Plan(
            goal=Goal("Test"),
            tasks=[task_a, task_b],
        )

        task_b.dependencies = []
        plan.task_graph.edges["task-b"] = ["task-a"]

        result = validator.validate(plan)

        assert result["valid"] is False

    def test_plan_graph_mismatch(self):
        validator = PlanValidator()
        plan = make_valid_plan()

        plan.task_graph.tasks.clear()
        plan.task_graph.edges.clear()

        result = validator.validate(plan)

        assert result["valid"] is False


class TestPlanValidatorLimits:
    def test_max_errors(self):
        validator = PlanValidator(max_errors=1)

        plan = make_valid_plan()
        plan.goal = None
        plan.tasks = []

        result = validator.validate(plan)

        assert result["valid"] is False
        assert len(result["errors"]) == 1

    def test_max_warnings(self):
        validator = PlanValidator(max_warnings=0)

        plan = make_valid_plan()
        plan.constraints = None

        result = validator.validate(plan)

        assert result["valid"] is True
        assert result["warnings"] == []


class TestPlanValidatorStatistics:
    def test_statistics_returns_copy(self):
        validator = PlanValidator()
        validator.validate(make_valid_plan())

        statistics = validator.statistics()
        statistics["validation_count"] = 999

        assert validator.statistics()["validation_count"] == 1

    def test_reset_statistics(self):
        validator = PlanValidator()
        validator.validate(make_valid_plan())

        validator.reset_statistics()

        assert validator.statistics() == {
            "validation_count": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "error_count": 0,
            "warning_count": 0,
        }

    def test_diagnostics(self):
        validator = PlanValidator()
        validator.validate(make_valid_plan())

        diagnostics = validator.diagnostics()

        assert diagnostics["validator"] == "PlanValidator"
        assert diagnostics["version"] == "1.0.0"
        assert diagnostics["strict"] is False
        assert "statistics" in diagnostics
        assert "report" in diagnostics

    def test_repr(self):
        validator = PlanValidator()

        assert "PlanValidator" in repr(validator)

    def test_str(self):
        validator = PlanValidator()

        assert "PlanValidator" in str(validator)
