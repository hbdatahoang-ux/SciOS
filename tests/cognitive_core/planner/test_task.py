import pytest

from scios.cognitive_core.planner.task import Task


# ==========================================================
# Initialization
# ==========================================================


def test_task_default_creation() -> None:
    task = Task("Analyze experiment")

    assert task.id is None
    assert task.description == "Analyze experiment"
    assert task.constraints == {}
    assert task.dependencies == []
    assert task.metadata == {}


def test_task_creation_with_all_fields() -> None:
    task = Task(
        description="Run simulation",
        constraints={"priority": 10, "budget": 100},
        dependencies=["task-a", "task-b"],
        task_id="task-c",
    )

    assert task.id == "task-c"
    assert task.description == "Run simulation"
    assert task.constraints == {
        "priority": 10,
        "budget": 100,
    }
    assert task.dependencies == [
        "task-a",
        "task-b",
    ]


def test_task_copies_constraints() -> None:
    constraints = {"priority": 10}

    task = Task(
        "Task",
        constraints=constraints,
    )

    constraints["priority"] = 99

    assert task.constraints["priority"] == 10


def test_task_copies_dependencies() -> None:
    dependencies = ["task-a"]

    task = Task(
        "Task",
        dependencies=dependencies,
    )

    dependencies.append("task-b")

    assert task.dependencies == ["task-a"]


def test_task_rejects_invalid_description() -> None:
    with pytest.raises(TypeError):
        Task(123)  # type: ignore[arg-type]


def test_task_rejects_invalid_constraints() -> None:
    with pytest.raises(TypeError):
        Task(
            "Task",
            constraints=[],  # type: ignore[arg-type]
        )


def test_task_rejects_invalid_dependencies() -> None:
    with pytest.raises(TypeError):
        Task(
            "Task",
            dependencies={},  # type: ignore[arg-type]
        )


def test_task_rejects_non_string_dependencies() -> None:
    with pytest.raises(TypeError):
        Task(
            "Task",
            dependencies=["task-a", 123],  # type: ignore[list-item]
        )


def test_task_rejects_invalid_task_id() -> None:
    with pytest.raises(TypeError):
        Task(
            "Task",
            task_id=123,  # type: ignore[arg-type]
        )


# ==========================================================
# Constraint Management
# ==========================================================


def test_add_constraint() -> None:
    task = Task("Task")

    task.add_constraint("priority", 10)

    assert task.constraints["priority"] == 10


def test_add_constraint_replaces_existing_value() -> None:
    task = Task("Task")

    task.add_constraint("priority", 10)
    task.add_constraint("priority", 20)

    assert task.get_constraint("priority") == 20


def test_add_constraint_rejects_invalid_key() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.add_constraint(123, "value")  # type: ignore[arg-type]


def test_get_constraint_with_default() -> None:
    task = Task("Task")

    assert task.get_constraint("missing") is None
    assert task.get_constraint("missing", 42) == 42


def test_get_constraint_rejects_invalid_key() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.get_constraint(123)  # type: ignore[arg-type]


def test_has_constraint() -> None:
    task = Task("Task")

    task.add_constraint("priority", 10)

    assert task.has_constraint("priority") is True
    assert task.has_constraint("missing") is False


def test_has_constraint_rejects_invalid_key() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.has_constraint(123)  # type: ignore[arg-type]


def test_remove_constraint() -> None:
    task = Task(
        "Task",
        constraints={"priority": 10},
    )

    task.remove_constraint("priority")

    assert task.has_constraint("priority") is False


def test_remove_missing_constraint_is_safe() -> None:
    task = Task("Task")

    task.remove_constraint("missing")

    assert task.constraints == {}


def test_remove_constraint_rejects_invalid_key() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.remove_constraint(123)  # type: ignore[arg-type]


# ==========================================================
# Dependency Management
# ==========================================================


def test_add_dependency() -> None:
    task = Task(
        "Task",
        task_id="task-b",
    )

    task.add_dependency("task-a")

    assert task.dependencies == ["task-a"]


def test_add_dependency_is_idempotent() -> None:
    task = Task(
        "Task",
        task_id="task-b",
    )

    task.add_dependency("task-a")
    task.add_dependency("task-a")

    assert task.dependencies == ["task-a"]


def test_add_dependency_rejects_non_string() -> None:
    task = Task(
        "Task",
        task_id="task-b",
    )

    with pytest.raises(TypeError):
        task.add_dependency(123)  # type: ignore[arg-type]


def test_task_cannot_depend_on_itself() -> None:
    task = Task(
        "Task",
        task_id="task-a",
    )

    with pytest.raises(ValueError):
        task.add_dependency("task-a")


def test_task_without_id_can_add_dependency() -> None:
    task = Task("Task")

    task.add_dependency("task-a")

    assert task.dependencies == ["task-a"]


def test_remove_dependency() -> None:
    task = Task(
        "Task",
        dependencies=["task-a", "task-b"],
    )

    task.remove_dependency("task-a")

    assert task.dependencies == ["task-b"]


def test_remove_missing_dependency_is_safe() -> None:
    task = Task("Task")

    task.remove_dependency("missing")

    assert task.dependencies == []


def test_remove_dependency_rejects_non_string() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.remove_dependency(123)  # type: ignore[arg-type]


def test_has_dependency() -> None:
    task = Task(
        "Task",
        dependencies=["task-a"],
    )

    assert task.has_dependency("task-a") is True
    assert task.has_dependency("task-b") is False


def test_has_dependency_rejects_non_string() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.has_dependency(123)  # type: ignore[arg-type]


# ==========================================================
# Metadata
# ==========================================================


def test_set_metadata() -> None:
    task = Task("Task")

    task.set_metadata("source", "planner")

    assert task.metadata["source"] == "planner"


def test_set_metadata_replaces_existing_value() -> None:
    task = Task("Task")

    task.set_metadata("priority", 10)
    task.set_metadata("priority", 20)

    assert task.get_metadata("priority") == 20


def test_set_metadata_rejects_invalid_key() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.set_metadata(123, "value")  # type: ignore[arg-type]


def test_get_metadata_with_default() -> None:
    task = Task("Task")

    assert task.get_metadata("missing") is None
    assert task.get_metadata("missing", "default") == "default"


def test_get_metadata_rejects_invalid_key() -> None:
    task = Task("Task")

    with pytest.raises(TypeError):
        task.get_metadata(123)  # type: ignore[arg-type]


# ==========================================================
# Serialization
# ==========================================================


def test_to_dict() -> None:
    task = Task(
        description="Run simulation",
        constraints={"priority": 10},
        dependencies=["task-a"],
        task_id="task-b",
    )

    task.set_metadata("source", "planner")

    assert task.to_dict() == {
        "id": "task-b",
        "description": "Run simulation",
        "constraints": {"priority": 10},
        "dependencies": ["task-a"],
        "metadata": {"source": "planner"},
    }


def test_to_dict_returns_copies() -> None:
    task = Task(
        "Task",
        constraints={"priority": 10},
        dependencies=["task-a"],
    )
    task.set_metadata("source", "planner")

    data = task.to_dict()

    data["constraints"]["priority"] = 99
    data["dependencies"].append("task-b")
    data["metadata"]["source"] = "runtime"

    assert task.constraints["priority"] == 10
    assert task.dependencies == ["task-a"]
    assert task.metadata["source"] == "planner"


def test_from_dict() -> None:
    data = {
        "id": "task-b",
        "description": "Run simulation",
        "constraints": {"priority": 10},
        "dependencies": ["task-a"],
        "metadata": {"source": "planner"},
    }

    task = Task.from_dict(data)

    assert task.id == "task-b"
    assert task.description == "Run simulation"
    assert task.constraints == {"priority": 10}
    assert task.dependencies == ["task-a"]
    assert task.metadata == {"source": "planner"}


def test_from_dict_round_trip() -> None:
    original = Task(
        description="Run simulation",
        constraints={"priority": 10},
        dependencies=["task-a"],
        task_id="task-b",
    )
    original.set_metadata("source", "planner")

    restored = Task.from_dict(original.to_dict())

    assert restored.to_dict() == original.to_dict()


def test_from_dict_rejects_non_dict() -> None:
    with pytest.raises(TypeError):
        Task.from_dict(None)  # type: ignore[arg-type]


def test_from_dict_rejects_invalid_metadata() -> None:
    data = {
        "id": "task-a",
        "description": "Task",
        "metadata": [],
    }

    with pytest.raises(TypeError):
        Task.from_dict(data)


# ==========================================================
# Representation / Architecture
# ==========================================================


def test_repr() -> None:
    task = Task(
        description="Run simulation",
        task_id="task-1",
    )

    result = repr(task)

    assert "Task" in result
    assert "task-1" in result
    assert "Run simulation" in result


def test_task_has_no_execution_state() -> None:
    task = Task("Run simulation")

    for attribute in (
        "status",
        "result",
        "started_at",
        "completed_at",
        "error",
        "retry_count",
        "execution_context",
    ):
        assert not hasattr(task, attribute)