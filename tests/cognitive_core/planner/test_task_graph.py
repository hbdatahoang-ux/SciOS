import pytest

from scios.cognitive_core.planner.task import Task
from scios.cognitive_core.planner.task_graph import TaskGraph


# ==========================================================
# Initialization
# ==========================================================


def test_task_graph_starts_empty() -> None:
    graph = TaskGraph()

    assert graph.tasks == {}
    assert graph.edges == {}
    assert len(graph) == 0
    assert graph.task_count == 0
    assert graph.edge_count == 0


# ==========================================================
# Task Registration
# ==========================================================


def test_add_task() -> None:
    graph = TaskGraph()
    task = Task("Task A", task_id="a")

    graph.add_task("a", task)

    assert graph.tasks["a"] is task
    assert graph.edges["a"] == []
    assert task.id == "a"
    assert len(graph) == 1


def test_add_task_assigns_missing_task_id() -> None:
    graph = TaskGraph()
    task = Task("Task A")

    graph.add_task("a", task)

    assert task.id == "a"
    assert graph.get_task("a") is task


def test_add_task_rejects_invalid_task_id() -> None:
    graph = TaskGraph()

    with pytest.raises(TypeError):
        graph.add_task(123, Task("Task"))  # type: ignore[arg-type]


def test_add_task_rejects_invalid_task() -> None:
    graph = TaskGraph()

    with pytest.raises(TypeError):
        graph.add_task("a", "invalid")  # type: ignore[arg-type]


def test_add_duplicate_task_rejected() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    with pytest.raises(ValueError):
        graph.add_task(
            "a",
            Task("Task A2", task_id="a"),
        )


def test_add_task_id_mismatch_rejected() -> None:
    graph = TaskGraph()

    task = Task(
        "Task A",
        task_id="different",
    )

    with pytest.raises(ValueError):
        graph.add_task("a", task)

    assert graph.tasks == {}
    assert graph.edges == {}


def test_add_task_with_unknown_dependency_rejected() -> None:
    graph = TaskGraph()

    task = Task(
        "Task B",
        dependencies=["a"],
        task_id="b",
    )

    with pytest.raises(ValueError):
        graph.add_task("b", task)

    assert graph.tasks == {}
    assert graph.edges == {}


def test_add_task_with_self_dependency_rejected() -> None:
    graph = TaskGraph()

    task = Task(
        "Task A",
        dependencies=["a"],
        task_id="a",
    )

    with pytest.raises(ValueError):
        graph.add_task("a", task)

    assert graph.tasks == {}
    assert graph.edges == {}


def test_add_task_preserves_existing_dependencies() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    task_b = Task(
        "Task B",
        dependencies=["a"],
        task_id="b",
    )

    graph.add_task("b", task_b)

    assert graph.edges["b"] == ["a"]
    assert task_b.dependencies == ["a"]


# ==========================================================
# Dependency Management
# ==========================================================


def test_add_dependency() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )

    graph.add_dependency("b", "a")

    assert graph.edges["b"] == ["a"]
    assert graph.get_dependencies("b") == ["a"]
    assert graph.tasks["b"].dependencies == ["a"]


def test_add_dependency_is_idempotent() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )

    graph.add_dependency("b", "a")
    graph.add_dependency("b", "a")

    assert graph.edges["b"] == ["a"]
    assert graph.tasks["b"].dependencies == ["a"]
    assert graph.edge_count == 1


def test_add_dependency_rejects_unknown_task() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    with pytest.raises(ValueError):
        graph.add_dependency("missing", "a")


def test_add_dependency_rejects_unknown_dependency() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    with pytest.raises(ValueError):
        graph.add_dependency("a", "missing")


def test_add_dependency_rejects_self_dependency() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    with pytest.raises(ValueError):
        graph.add_dependency("a", "a")


def test_add_dependency_rejects_invalid_task_id() -> None:
    graph = TaskGraph()

    with pytest.raises(TypeError):
        graph.add_dependency(
            123,  # type: ignore[arg-type]
            "a",
        )


def test_add_dependency_rejects_invalid_dependency_id() -> None:
    graph = TaskGraph()

    with pytest.raises(TypeError):
        graph.add_dependency(
            "a",
            123,  # type: ignore[arg-type]
        )


def test_remove_dependency() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )

    graph.add_dependency("b", "a")
    graph.remove_dependency("b", "a")

    assert graph.edges["b"] == []
    assert graph.tasks["b"].dependencies == []
    assert graph.edge_count == 0


def test_remove_missing_dependency_is_safe() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )

    graph.remove_dependency("b", "a")

    assert graph.edges["b"] == []


def test_remove_dependency_rejects_unknown_task() -> None:
    graph = TaskGraph()

    with pytest.raises(ValueError):
        graph.remove_dependency("missing", "a")


def test_remove_dependency_rejects_unknown_dependency() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    with pytest.raises(ValueError):
        graph.remove_dependency("a", "missing")


# ==========================================================
# Queries
# ==========================================================


def test_get_task() -> None:
    graph = TaskGraph()
    task = Task("Task A", task_id="a")

    graph.add_task("a", task)

    assert graph.get_task("a") is task


def test_get_missing_task_returns_none() -> None:
    graph = TaskGraph()

    assert graph.get_task("missing") is None


def test_get_task_rejects_invalid_id() -> None:
    graph = TaskGraph()

    with pytest.raises(TypeError):
        graph.get_task(123)  # type: ignore[arg-type]


def test_get_dependencies_returns_copy() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )
    graph.add_dependency("b", "a")

    dependencies = graph.get_dependencies("b")
    dependencies.append("fake")

    assert graph.edges["b"] == ["a"]


def test_get_dependencies_unknown_task_returns_empty_list() -> None:
    graph = TaskGraph()

    assert graph.get_dependencies("missing") == []


def test_has_task() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    assert graph.has_task("a") is True
    assert graph.has_task("missing") is False


def test_has_task_rejects_invalid_id() -> None:
    graph = TaskGraph()

    with pytest.raises(TypeError):
        graph.has_task(123)  # type: ignore[arg-type]


# ==========================================================
# Compatibility Graph View
# ==========================================================


def test_graph_property() -> None:
    graph = TaskGraph()

    task_a = Task("Task A", task_id="a")
    task_b = Task("Task B", task_id="b")

    graph.add_task("a", task_a)
    graph.add_task("b", task_b)
    graph.add_dependency("b", "a")

    view = graph.graph

    assert view["a"]["task"] is task_a
    assert view["a"]["dependencies"] == []
    assert view["b"]["task"] is task_b
    assert view["b"]["dependencies"] == ["a"]


def test_graph_property_returns_dependency_copies() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )
    graph.add_dependency("b", "a")

    view = graph.graph
    view["b"]["dependencies"].append("fake")

    assert graph.edges["b"] == ["a"]


# ==========================================================
# Topological Sort
# ==========================================================


def test_topological_sort_empty_graph() -> None:
    graph = TaskGraph()

    assert graph.topological_sort() == []


def test_topological_sort_single_task() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    assert graph.topological_sort() == ["a"]


def test_topological_sort_dependency_before_dependent() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )

    graph.add_dependency("b", "a")

    assert graph.topological_sort() == ["a", "b"]


def test_topological_sort_chain() -> None:
    graph = TaskGraph()

    for task_id in ("a", "b", "c"):
        graph.add_task(
            task_id,
            Task(
                f"Task {task_id}",
                task_id=task_id,
            ),
        )

    graph.add_dependency("b", "a")
    graph.add_dependency("c", "b")

    assert graph.topological_sort() == [
        "a",
        "b",
        "c",
    ]


def test_topological_sort_diamond() -> None:
    graph = TaskGraph()

    for task_id in ("a", "b", "c", "d"):
        graph.add_task(
            task_id,
            Task(
                f"Task {task_id}",
                task_id=task_id,
            ),
        )

    graph.add_dependency("b", "a")
    graph.add_dependency("c", "a")
    graph.add_dependency("d", "b")
    graph.add_dependency("d", "c")

    order = graph.topological_sort()

    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")


def test_topological_sort_detects_two_node_cycle() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )

    graph.add_dependency("b", "a")

    # Bypassing the public API here intentionally creates an
    # invalid structural state so cycle detection itself can be tested.
    graph.edges["a"].append("b")

    with pytest.raises(ValueError, match="dependency cycle"):
        graph.topological_sort()


def test_topological_sort_detects_long_cycle() -> None:
    graph = TaskGraph()

    for task_id in ("a", "b", "c"):
        graph.add_task(
            task_id,
            Task(
                f"Task {task_id}",
                task_id=task_id,
            ),
        )

    graph.add_dependency("b", "a")
    graph.add_dependency("c", "b")

    # Intentionally corrupt the graph to test cycle detection.
    graph.edges["a"].append("c")

    with pytest.raises(ValueError, match="dependency cycle"):
        graph.topological_sort()


def test_topological_sort_detects_unknown_dependency() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    # Intentionally corrupt the internal graph to test defensive
    # validation inside topological_sort().
    graph.edges["a"].append("missing")

    with pytest.raises(
        ValueError,
        match="Unknown dependency",
    ):
        graph.topological_sort()


# ==========================================================
# Clear / Counts
# ==========================================================


def test_clear() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )
    graph.add_dependency("b", "a")

    graph.clear()

    assert graph.tasks == {}
    assert graph.edges == {}
    assert len(graph) == 0
    assert graph.task_count == 0
    assert graph.edge_count == 0


def test_counts() -> None:
    graph = TaskGraph()

    for task_id in ("a", "b", "c"):
        graph.add_task(
            task_id,
            Task(
                f"Task {task_id}",
                task_id=task_id,
            ),
        )

    graph.add_dependency("b", "a")
    graph.add_dependency("c", "a")
    graph.add_dependency("c", "b")

    assert graph.task_count == 3
    assert graph.edge_count == 3


# ==========================================================
# Container / Representation
# ==========================================================


def test_contains() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )

    assert "a" in graph
    assert "missing" not in graph


def test_repr() -> None:
    graph = TaskGraph()

    graph.add_task(
        "a",
        Task("Task A", task_id="a"),
    )
    graph.add_task(
        "b",
        Task("Task B", task_id="b"),
    )
    graph.add_dependency("b", "a")

    result = repr(graph)

    assert "TaskGraph" in result
    assert "tasks=2" in result
    assert "edges=1" in result


def test_task_graph_has_no_execution_state() -> None:
    graph = TaskGraph()

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
    ):
        assert not hasattr(graph, attribute)