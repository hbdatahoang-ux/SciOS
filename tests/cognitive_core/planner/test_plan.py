import pytest

from scios.cognitive_core.planner.constraint import (
    Constraint,
    ConstraintSet,
)
from scios.cognitive_core.planner.goal import Goal
from scios.cognitive_core.planner.plan import Plan
from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.task_graph import TaskGraph


# ==========================================================
# Initialization
# ==========================================================


def test_plan_requires_goal() -> None:
    with pytest.raises(TypeError):
        Plan("invalid")  # type: ignore[arg-type]


def test_plan_default_creation() -> None:
    goal = Goal("Run experiment")
    plan = Plan(goal)

    assert plan.goal is goal
    assert plan.tasks == []
    assert isinstance(plan.task_graph, TaskGraph)
    assert isinstance(plan.constraints, ConstraintSet)
    assert plan.metadata == {}
    assert plan.task_count == 0
    assert plan.is_empty is True


def test_plan_accepts_tasks() -> None:
    goal = Goal("Run experiment")

    task_a = Task(
        "Prepare",
        task_id="a",
    )
    task_b = Task(
        "Execute",
        task_id="b",
        dependencies=["a"],
    )

    graph = TaskGraph()
    graph.add_task("a", task_a)
    graph.add_task("b", task_b)

    plan = Plan(
        goal,
        tasks=[task_a, task_b],
        task_graph=graph,
    )

    assert plan.tasks == [task_a, task_b]
    assert plan.task_graph is graph


def test_plan_rejects_non_list_tasks() -> None:
    with pytest.raises(TypeError):
        Plan(
            Goal("Goal"),
            tasks={},  # type: ignore[arg-type]
        )


def test_plan_rejects_invalid_task_items() -> None:
    with pytest.raises(TypeError):
        Plan(
            Goal("Goal"),
            tasks=["invalid"],  # type: ignore[list-item]
        )


def test_plan_rejects_invalid_task_graph() -> None:
    with pytest.raises(TypeError):
        Plan(
            Goal("Goal"),
            task_graph={},  # type: ignore[arg-type]
        )


def test_plan_rejects_invalid_constraint_set() -> None:
    with pytest.raises(TypeError):
        Plan(
            Goal("Goal"),
            constraints={},  # type: ignore[arg-type]
        )


# ==========================================================
# Task Identity
# ==========================================================


def test_add_task_preserves_existing_task_id() -> None:
    plan = Plan(Goal("Goal"))
    task = Task(
        "Task A",
        task_id="a",
    )

    plan.add_task(task)

    assert task.id == "a"
    assert plan.get_task("a") is task


def test_add_task_allocates_id_when_missing() -> None:
    plan = Plan(Goal("Goal"))
    task = Task("Task A")

    plan.add_task(task)

    assert task.id == "task-0"
    assert plan.get_task("task-0") is task


def test_add_multiple_tasks_allocates_deterministic_ids() -> None:
    plan = Plan(Goal("Goal"))

    task_a = Task("Task A")
    task_b = Task("Task B")
    task_c = Task("Task C")

    plan.add_task(task_a)
    plan.add_task(task_b)
    plan.add_task(task_c)

    assert task_a.id == "task-0"
    assert task_b.id == "task-1"
    assert task_c.id == "task-2"


def test_add_task_with_explicit_id() -> None:
    plan = Plan(Goal("Goal"))
    task = Task("Task A")

    plan.add_task(
        task,
        task_id="custom-id",
    )

    assert task.id == "custom-id"
    assert plan.has_task("custom-id")


def test_add_task_id_mismatch_rejected() -> None:
    plan = Plan(Goal("Goal"))
    task = Task(
        "Task A",
        task_id="original",
    )

    with pytest.raises(ValueError):
        plan.add_task(
            task,
            task_id="different",
        )

    assert plan.tasks == []
    assert plan.task_graph.tasks == {}


def test_duplicate_task_object_is_ignored() -> None:
    plan = Plan(Goal("Goal"))
    task = Task(
        "Task A",
        task_id="a",
    )

    plan.add_task(task)
    plan.add_task(task)

    assert len(plan.tasks) == 1
    assert plan.task_count == 1


def test_duplicate_task_id_is_rejected() -> None:
    plan = Plan(Goal("Goal"))

    plan.add_task(
        Task("Task A", task_id="a"),
    )

    with pytest.raises(ValueError):
        plan.add_task(
            Task("Task B", task_id="a"),
        )

    assert plan.task_count == 1


# ==========================================================
# Dependency Integration
# ==========================================================


def test_add_task_registers_dependencies_in_graph() -> None:
    plan = Plan(Goal("Goal"))

    task_a = Task(
        "Task A",
        task_id="a",
    )

    task_b = Task(
        "Task B",
        task_id="b",
        dependencies=["a"],
    )

    plan.add_task(task_a)
    plan.add_task(task_b)

    assert plan.task_graph.get_dependencies("b") == ["a"]
    assert task_b.dependencies == ["a"]


def test_add_task_with_unknown_dependency_is_rejected() -> None:
    plan = Plan(Goal("Goal"))

    task = Task(
        "Task B",
        task_id="b",
        dependencies=["missing"],
    )

    with pytest.raises(ValueError, match="Unknown dependency"):
        plan.add_task(task)

    assert plan.tasks == []
    assert plan.task_graph.tasks == {}


def test_dependency_order() -> None:
    plan = Plan(Goal("Goal"))

    task_a = Task(
        "Task A",
        task_id="a",
    )
    task_b = Task(
        "Task B",
        task_id="b",
        dependencies=["a"],
    )
    task_c = Task(
        "Task C",
        task_id="c",
        dependencies=["b"],
    )

    plan.add_task(task_a)
    plan.add_task(task_b)
    plan.add_task(task_c)

    assert [
        task.id
        for task in plan.topological_order()
    ] == ["a", "b", "c"]


def test_topological_order_is_structural_not_runtime() -> None:
    plan = Plan(Goal("Goal"))

    plan.add_task(
        Task(
            "Task A",
            task_id="a",
        )
    )

    ordered = plan.topological_order()

    assert ordered[0].id == "a"

    for attribute in (
        "status",
        "result",
        "started_at",
        "completed_at",
        "error",
        "retry_count",
        "execution_context",
    ):
        assert not hasattr(ordered[0], attribute)


# ==========================================================
# Task Queries
# ==========================================================


def test_get_task() -> None:
    plan = Plan(Goal("Goal"))
    task = Task(
        "Task A",
        task_id="a",
    )

    plan.add_task(task)

    assert plan.get_task("a") is task


def test_get_missing_task_returns_none() -> None:
    plan = Plan(Goal("Goal"))

    assert plan.get_task("missing") is None


def test_get_task_rejects_invalid_id() -> None:
    plan = Plan(Goal("Goal"))

    with pytest.raises(TypeError):
        plan.get_task(123)  # type: ignore[arg-type]


def test_has_task() -> None:
    plan = Plan(Goal("Goal"))
    plan.add_task(
        Task(
            "Task A",
            task_id="a",
        )
    )

    assert plan.has_task("a") is True
    assert plan.has_task("missing") is False


def test_contains_task() -> None:
    plan = Plan(Goal("Goal"))
    plan.add_task(
        Task(
            "Task A",
            task_id="a",
        )
    )

    assert "a" in plan
    assert "missing" not in plan


# ==========================================================
# Task Removal
# ==========================================================


def test_remove_task() -> None:
    plan = Plan(Goal("Goal"))

    task_a = Task(
        "Task A",
        task_id="a",
    )
    task_b = Task(
        "Task B",
        task_id="b",
        dependencies=["a"],
    )

    plan.add_task(task_a)
    plan.add_task(task_b)

    removed = plan.remove_task("a")

    assert removed is task_a
    assert plan.get_task("a") is None
    assert plan.task_count == 1
    assert plan.task_graph.get_dependencies("b") == []
    assert task_b.dependencies == []


def test_remove_missing_task_returns_none() -> None:
    plan = Plan(Goal("Goal"))

    assert plan.remove_task("missing") is None


def test_remove_task_rejects_invalid_id() -> None:
    plan = Plan(Goal("Goal"))

    with pytest.raises(TypeError):
        plan.remove_task(123)  # type: ignore[arg-type]


# ==========================================================
# Metadata
# ==========================================================


def test_set_metadata() -> None:
    plan = Plan(Goal("Goal"))

    plan.set_metadata(
        "strategy",
        "priority",
    )

    assert plan.metadata["strategy"] == "priority"


def test_set_metadata_replaces_value() -> None:
    plan = Plan(Goal("Goal"))

    plan.set_metadata("strategy", "fifo")
    plan.set_metadata("strategy", "priority")

    assert plan.get_metadata("strategy") == "priority"


def test_get_metadata_with_default() -> None:
    plan = Plan(Goal("Goal"))

    assert plan.get_metadata("missing") is None
    assert plan.get_metadata("missing", 42) == 42


def test_metadata_rejects_invalid_key() -> None:
    plan = Plan(Goal("Goal"))

    with pytest.raises(TypeError):
        plan.set_metadata(123, "value")  # type: ignore[arg-type]


def test_get_metadata_rejects_invalid_key() -> None:
    plan = Plan(Goal("Goal"))

    with pytest.raises(TypeError):
        plan.get_metadata(123)  # type: ignore[arg-type]


# ==========================================================
# Constraints
# ==========================================================


def test_plan_accepts_constraint_set() -> None:
    constraints = ConstraintSet()
    constraints.add_constraint(
        Constraint(
            "budget",
            1000,
        )
    )

    plan = Plan(
        Goal("Goal"),
        constraints=constraints,
    )

    assert plan.constraints is constraints
    assert plan.constraints.get_constraint("budget") is not None


# ==========================================================
# Serialization
# ==========================================================


def test_to_dict() -> None:
    plan = Plan(
        Goal(
            "Run experiment",
            success_criteria=["completed"],
        )
    )

    task = Task(
        "Prepare experiment",
        task_id="task-1",
        constraints={"priority": 10},
    )
    task.set_metadata(
        "source",
        "planner",
    )

    plan.add_task(task)

    plan.set_metadata(
        "strategy",
        "priority",
    )

    data = plan.to_dict()

    assert data == {
        "goal": {
            "description": "Run experiment",
            "success_criteria": ["completed"],
            "constraints": {},
        },
        "tasks": [
            {
                "id": "task-1",
                "description": "Prepare experiment",
                "constraints": {"priority": 10},
                "dependencies": [],
                "metadata": {"source": "planner"},
            }
        ],
        "constraints": {},
        "metadata": {
            "strategy": "priority",
        },
    }


def test_to_dict_does_not_duplicate_task_graph() -> None:
    plan = Plan(Goal("Goal"))

    task_a = Task(
        "Task A",
        task_id="a",
    )
    task_b = Task(
        "Task B",
        task_id="b",
        dependencies=["a"],
    )

    plan.add_task(task_a)
    plan.add_task(task_b)

    data = plan.to_dict()

    assert "task_graph" not in data
    assert data["tasks"][1]["dependencies"] == ["a"]


def test_to_dict_returns_metadata_copy() -> None:
    plan = Plan(Goal("Goal"))
    plan.set_metadata("source", "planner")

    data = plan.to_dict()
    data["metadata"]["source"] = "runtime"

    assert plan.metadata["source"] == "planner"


# ==========================================================
# Structural Invariants
# ==========================================================


def test_plan_task_list_and_graph_are_synchronized() -> None:
    plan = Plan(Goal("Goal"))

    task_a = Task(
        "Task A",
        task_id="a",
    )
    task_b = Task(
        "Task B",
        task_id="b",
    )

    plan.add_task(task_a)
    plan.add_task(task_b)

    assert set(task.id for task in plan.tasks) == set(
        plan.task_graph.tasks
    )


def test_plan_has_no_execution_state() -> None:
    plan = Plan(Goal("Goal"))

    for attribute in (
        "status",
        "result",
        "started_at",
        "completed_at",
        "error",
        "retry_count",
        "execution_context",
        "scheduler",
        "executor",
        "execution_graph",
    ):
        assert not hasattr(plan, attribute)


# ==========================================================
# Representation
# ==========================================================


def test_len() -> None:
    plan = Plan(Goal("Goal"))

    assert len(plan) == 0

    plan.add_task(
        Task(
            "Task A",
            task_id="a",
        )
    )

    assert len(plan) == 1


def test_repr() -> None:
    plan = Plan(
        Goal("Run experiment"),
    )

    plan.add_task(
        Task(
            "Prepare",
            task_id="prepare",
        )
    )

    result = repr(plan)

    assert "Plan" in result
    assert "Run experiment" in result
    assert "tasks=1" in result