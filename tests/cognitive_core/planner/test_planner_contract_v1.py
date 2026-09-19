from __future__ import annotations

import inspect

import pytest

from scios.cognitive_core.planner import (
    Goal,
    Plan,
    Planner,
    PlanningPolicy,
    PlanningStrategy,
    Task,
    TaskGraph,
)


# ============================================================
# Planner vNext Contract v1.0
# ============================================================


def test_contract_version_is_explicit():
    from scios.cognitive_core import planner as planner_pkg

    assert getattr(
        planner_pkg,
        "PLANNER_CONTRACT_VERSION",
        None,
    ) == "1.0"


# ============================================================
# P1 — Planner is a pure planning component
# ============================================================


def test_planner_create_plan_returns_plan():
    goal = Goal(
        "Analyze experiment",
        success_criteria=[
            "data_valid",
            "model_fit",
        ],
    )

    planner = Planner()
    plan = planner.create_plan(goal)

    assert isinstance(plan, Plan)
    assert plan.goal is goal


def test_planner_has_no_execution_api():
    planner = Planner()

    assert not hasattr(planner, "run")
    assert not hasattr(planner, "execute")


def test_planner_has_no_execution_state():
    planner = Planner()

    forbidden_attributes = (
        "state",
        "status",
        "history",
        "execution",
        "executor",
        "monitor",
        "recovery",
    )

    for attribute in forbidden_attributes:
        assert not hasattr(planner, attribute), attribute


def test_planner_create_plan_does_not_execute():
    goal = Goal(
        "Analyze experiment",
        success_criteria=[
            "data_valid",
            "model_fit",
        ],
    )

    plan = Planner().create_plan(goal)

    assert isinstance(plan, Plan)
    assert plan.tasks

    for task in plan.tasks:
        assert not hasattr(task, "completed")
        assert not hasattr(task, "status")
        assert not hasattr(task, "start")
        assert not hasattr(task, "mark_completed")
        assert not hasattr(task, "mark_failed")


# ============================================================
# P2 — Planner produces the canonical Cognitive Plan
# ============================================================


def test_planner_accepts_explicit_tasks():
    goal = Goal("Test goal")

    tasks = [
        Task("Task A"),
        Task("Task B"),
    ]

    plan = Planner().create_plan(
        goal,
        tasks,
    )

    assert isinstance(plan, Plan)
    assert plan.tasks == tasks


def test_planner_converts_string_tasks_to_task_objects():
    goal = Goal("Test goal")

    plan = Planner().create_plan(
        goal,
        ["Task A", "Task B"],
    )

    assert all(
        isinstance(task, Task)
        for task in plan.tasks
    )

    assert [
        task.description
        for task in plan.tasks
    ] == [
        "Task A",
        "Task B",
    ]


def test_planner_preserves_explicit_task_identity():
    goal = Goal("Test goal")

    task_a = Task(
        "Task A",
        task_id="a",
    )

    task_b = Task(
        "Task B",
        task_id="b",
    )

    plan = Planner().create_plan(
        goal,
        [task_a, task_b],
    )

    assert plan.tasks[0] is task_a
    assert plan.tasks[1] is task_b


def test_planner_rejects_invalid_goal():
    planner = Planner()

    with pytest.raises(TypeError):
        planner.create_plan("not a Goal")


def test_planner_rejects_invalid_task_items():
    planner = Planner()
    goal = Goal("Test goal")

    with pytest.raises(TypeError):
        planner.create_plan(
            goal,
            [Task("A"), 123],
        )


# ============================================================
# P3 — Task is a planning domain object
# ============================================================


def test_task_has_planning_identity_and_description():
    task = Task(
        "Analyze data",
        task_id="analyze",
    )

    assert task.id == "analyze"
    assert task.description == "Analyze data"


def test_task_preserves_dependencies():
    task = Task(
        "Analyze model",
        task_id="model",
        dependencies=["data"],
    )

    assert task.dependencies == ["data"]


def test_task_preserves_constraints():
    task = Task(
        "Analyze model",
        task_id="model",
        constraints={
            "priority": 10,
        },
    )

    assert task.constraints == {
        "priority": 10,
    }


def test_task_has_no_execution_lifecycle():
    task = Task("Pending task")

    forbidden_attributes = (
        "completed",
        "status",
        "start",
        "mark_completed",
        "mark_failed",
        "is_completed",
        "is_running",
        "is_failed",
    )

    for attribute in forbidden_attributes:
        assert not hasattr(task, attribute), attribute


# ============================================================
# P4 — Plan is a planning artifact, not an execution record
# ============================================================


def test_plan_accepts_unexecuted_tasks():
    goal = Goal("Test goal")
    task = Task("Pending task")

    plan = Plan(
        goal=goal,
        tasks=[task],
    )

    assert plan.goal is goal
    assert plan.tasks == [task]


def test_plan_has_no_execution_api():
    goal = Goal("Test goal")

    plan = Plan(
        goal=goal,
        tasks=[Task("Pending task")],
    )

    assert not hasattr(plan, "execute")
    assert not hasattr(plan, "run")
    assert not hasattr(plan, "is_completed")


def test_plan_has_no_execution_status():
    goal = Goal("Test goal")

    plan = Plan(
        goal=goal,
        tasks=[Task("Pending task")],
    )

    assert not hasattr(plan, "status")
    assert not hasattr(plan, "execution")
    assert not hasattr(plan, "executor")
    assert not hasattr(plan, "progress")


def test_plan_registers_tasks_in_task_graph():
    goal = Goal("Test goal")

    task_a = Task(
        "Task A",
        task_id="a",
    )

    task_b = Task(
        "Task B",
        task_id="b",
    )

    plan = Plan(
        goal=goal,
        tasks=[task_a, task_b],
    )

    assert plan.task_graph.get_task("a") is task_a
    assert plan.task_graph.get_task("b") is task_b


# ============================================================
# P5 — TaskGraph is a DAG
# ============================================================


def test_task_graph_preserves_dependencies():
    task_a = Task("A", task_id="a")
    task_b = Task("B", task_id="b")
    task_c = Task("C", task_id="c")

    graph = TaskGraph()

    graph.add_task("a", task_a)
    graph.add_task("b", task_b)
    graph.add_task("c", task_c)

    graph.add_dependency("c", "a")
    graph.add_dependency("c", "b")

    order = graph.topological_sort()

    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("c")


def test_task_graph_rejects_cycle():
    task_a = Task("A", task_id="a")
    task_b = Task("B", task_id="b")

    graph = TaskGraph()

    graph.add_task("a", task_a)
    graph.add_task("b", task_b)

    graph.add_dependency("a", "b")
    graph.add_dependency("b", "a")

    with pytest.raises(ValueError):
        graph.topological_sort()


def test_task_graph_rejects_unknown_dependency():
    task_a = Task("A", task_id="a")

    graph = TaskGraph()
    graph.add_task("a", task_a)

    with pytest.raises(ValueError):
        graph.add_dependency("a", "missing")


def test_task_graph_contains_only_registered_tasks():
    task_a = Task("A", task_id="a")

    graph = TaskGraph()
    graph.add_task("a", task_a)

    assert set(graph.tasks) == {"a"}
    assert set(graph.edges) == {"a"}


# ============================================================
# P6 — PlanningPolicy must not violate dependencies
# ============================================================


def test_policy_preserves_dependency_order():
    task_a = Task(
        "A",
        task_id="a",
        constraints={"priority": 1},
    )

    task_b = Task(
        "B",
        task_id="b",
        constraints={"priority": 100},
    )

    task_c = Task(
        "C",
        task_id="c",
        constraints={"priority": 1000},
    )

    graph = TaskGraph()

    graph.add_task("a", task_a)
    graph.add_task("b", task_b)
    graph.add_task("c", task_c)

    graph.add_dependency("c", "a")
    graph.add_dependency("c", "b")

    policy = PlanningPolicy()

    ordered = policy.apply(
        [task_a, task_b, task_c],
    )

    positions = {
        task.id: index
        for index, task in enumerate(ordered)
    }

    assert positions["a"] < positions["c"]
    assert positions["b"] < positions["c"]


def test_policy_preserves_all_tasks():
    tasks = [
        Task("A", task_id="a"),
        Task("B", task_id="b"),
        Task("C", task_id="c"),
    ]

    ordered = PlanningPolicy().apply(tasks)

    assert set(ordered) == set(tasks)
    assert len(ordered) == len(tasks)


# ============================================================
# P7 — Validator validates planning structure
# ============================================================


def test_validator_accepts_unexecuted_plan():
    from scios.cognitive_core.planner import PlanValidator

    goal = Goal("Pending work")

    task = Task(
        "Pending task",
        task_id="pending",
    )

    plan = Plan(
        goal=goal,
        tasks=[task],
    )

    result = PlanValidator().validate(plan)

    assert result["valid"] is True
    assert result["errors"] == []


def test_validator_rejects_empty_plan():
    from scios.cognitive_core.planner import PlanValidator

    goal = Goal("Empty plan")
    plan = Plan(goal=goal)

    result = PlanValidator().validate(plan)

    assert result["valid"] is False
    assert result["errors"]


def test_validator_does_not_require_execution_completion():
    from scios.cognitive_core.planner import PlanValidator

    goal = Goal("Structural validation")

    task = Task(
        "Unexecuted task",
        task_id="task",
    )

    plan = Plan(
        goal=goal,
        tasks=[task],
    )

    result = PlanValidator().validate(plan)

    assert result["valid"] is True


# ============================================================
# P8 — Strategy decomposition
# ============================================================


def test_strategy_decompose_goal_returns_tasks():
    goal = Goal(
        "Analyze experiment",
        success_criteria=[
            "data_valid",
            "model_fit",
        ],
    )

    strategy = PlanningStrategy()

    assert hasattr(strategy, "decompose_goal")

    tasks = strategy.decompose_goal(goal)

    assert isinstance(tasks, list)
    assert tasks

    assert all(
        isinstance(task, Task)
        for task in tasks
    )


def test_strategy_decomposition_is_deterministic():
    goal = Goal(
        "Analyze experiment",
        success_criteria=[
            "data_valid",
            "model_fit",
        ],
    )

    strategy = PlanningStrategy()

    tasks_a = strategy.decompose_goal(goal)
    tasks_b = strategy.decompose_goal(goal)

    assert [
        task.description
        for task in tasks_a
    ] == [
        task.description
        for task in tasks_b
    ]


def test_strategy_does_not_execute_tasks():
    goal = Goal(
        "Analyze experiment",
        success_criteria=[
            "data_valid",
        ],
    )

    tasks = PlanningStrategy().decompose_goal(goal)

    for task in tasks:
        assert not hasattr(task, "completed")
        assert not hasattr(task, "status")
        assert not hasattr(task, "mark_completed")
        assert not hasattr(task, "mark_failed")


# ============================================================
# P9 — Cognitive Planner runtime isolation
# ============================================================


def test_cognitive_planner_does_not_depend_on_runtime_agent():
    planner_module = inspect.getmodule(Planner)

    assert planner_module is not None

    source = inspect.getsource(planner_module)

    assert "scios.runtime.agent" not in source
    assert "runtime.agent" not in source


def test_cognitive_planner_has_no_runtime_execution_imports():
    planner_module = inspect.getmodule(Planner)

    assert planner_module is not None

    source = inspect.getsource(planner_module)

    forbidden_imports = (
        "ToolRouter",
        "ToolExecutor",
        "ToolRegistry",
        "ToolSandbox",
        "ExecutionEngine",
        "Agent",
    )

    for symbol in forbidden_imports:
        assert symbol not in source


# ============================================================
# P10 — Planner reset and representation
# ============================================================


def test_planner_reset_restores_default_strategy():
    planner = Planner()

    original_strategy = planner.strategy

    planner.reset()

    assert isinstance(
        planner.strategy,
        PlanningStrategy,
    )

    assert planner.strategy.name == "DefaultStrategy"
    assert planner.strategy is not original_strategy


def test_planner_repr_is_planning_oriented():
    planner = Planner()

    representation = repr(planner)

    assert "Planner" in representation
    assert "DefaultStrategy" in representation

    assert "executor" not in representation.lower()
    assert "execution" not in representation.lower()


# ============================================================
# P11 — Plan construction preserves canonical identity
# ============================================================


def test_plan_preserves_goal_identity():
    goal = Goal("Test goal")

    plan = Plan(
        goal=goal,
        tasks=[],
    )

    assert plan.goal is goal


def test_plan_preserves_task_identity():
    goal = Goal("Test goal")

    task = Task(
        "Task A",
        task_id="a",
    )

    plan = Plan(
        goal=goal,
        tasks=[task],
    )

    assert plan.tasks[0] is task


def test_plan_task_graph_and_tasks_are_consistent():
    goal = Goal("Test goal")

    task_a = Task(
        "Task A",
        task_id="a",
    )

    task_b = Task(
        "Task B",
        task_id="b",
    )

    plan = Plan(
        goal=goal,
        tasks=[
            task_a,
            task_b,
        ],
    )

    assert len(plan.tasks) == len(plan.task_graph.tasks)

    for task in plan.tasks:
        assert task.id is not None
        assert plan.task_graph.get_task(task.id) is task
