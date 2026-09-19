import pytest

from scios.cognitive_core.planner.constraint import (
    Constraint,
    ConstraintSet,
)


# ---------------------------------------------------------------------------
# Constraint
# ---------------------------------------------------------------------------


def test_constraint_default_type() -> None:
    constraint = Constraint("deadline", "2026-12-31")

    assert constraint.name == "deadline"
    assert constraint.value == "2026-12-31"
    assert constraint.constraint_type == "generic"


def test_constraint_custom_type() -> None:
    constraint = Constraint(
        "budget",
        1000,
        constraint_type="resource",
    )

    assert constraint.constraint_type == "resource"


def test_constraint_rejects_invalid_name() -> None:
    with pytest.raises(TypeError):
        Constraint(123, "value")  # type: ignore[arg-type]


def test_constraint_rejects_invalid_constraint_type() -> None:
    with pytest.raises(TypeError):
        Constraint(
            "budget",
            1000,
            constraint_type=123,  # type: ignore[arg-type]
        )


def test_constraint_is_satisfied_when_value_matches() -> None:
    constraint = Constraint("budget", 1000)

    assert constraint.is_satisfied({"budget": 1000}) is True


def test_constraint_is_not_satisfied_when_value_differs() -> None:
    constraint = Constraint("budget", 1000)

    assert constraint.is_satisfied({"budget": 900}) is False


def test_constraint_is_not_satisfied_when_key_missing() -> None:
    constraint = Constraint("budget", 1000)

    assert constraint.is_satisfied({}) is False


def test_constraint_accepts_none_as_value() -> None:
    constraint = Constraint("resource", None)

    assert constraint.is_satisfied({"resource": None}) is True
    assert constraint.is_satisfied({}) is False


def test_constraint_rejects_invalid_context() -> None:
    constraint = Constraint("budget", 1000)

    with pytest.raises(TypeError):
        constraint.is_satisfied(None)  # type: ignore[arg-type]


def test_constraint_to_dict() -> None:
    constraint = Constraint(
        "deadline",
        "2026-12-31",
        constraint_type="temporal",
    )

    assert constraint.to_dict() == {
        "name": "deadline",
        "value": "2026-12-31",
        "constraint_type": "temporal",
    }


def test_constraint_repr() -> None:
    constraint = Constraint(
        "budget",
        1000,
        constraint_type="resource",
    )

    result = repr(constraint)

    assert "Constraint" in result
    assert "budget" in result
    assert "1000" in result
    assert "resource" in result


def test_constraint_has_no_execution_state() -> None:
    constraint = Constraint("budget", 1000)

    for attribute in (
        "status",
        "result",
        "started_at",
        "completed_at",
        "error",
    ):
        assert not hasattr(constraint, attribute)


# ---------------------------------------------------------------------------
# ConstraintSet
# ---------------------------------------------------------------------------


def test_constraint_set_starts_empty() -> None:
    constraint_set = ConstraintSet()

    assert constraint_set.constraints == {}
    assert len(constraint_set) == 0


def test_constraint_set_accepts_initial_constraints() -> None:
    constraints = [
        Constraint("budget", 1000),
        Constraint("deadline", "2026-12-31"),
    ]

    constraint_set = ConstraintSet(constraints)

    assert len(constraint_set) == 2
    assert constraint_set.get_constraint("budget") is constraints[0]
    assert constraint_set.get_constraint("deadline") is constraints[1]


def test_constraint_set_add_constraint() -> None:
    constraint_set = ConstraintSet()
    constraint = Constraint("budget", 1000)

    constraint_set.add_constraint(constraint)

    assert constraint_set.constraints["budget"] is constraint
    assert len(constraint_set) == 1


def test_constraint_set_replaces_constraint_with_same_name() -> None:
    constraint_set = ConstraintSet()

    first = Constraint("budget", 1000)
    second = Constraint("budget", 2000)

    constraint_set.add_constraint(first)
    constraint_set.add_constraint(second)

    assert len(constraint_set) == 1
    assert constraint_set.get_constraint("budget") is second


def test_constraint_set_rejects_invalid_constraint() -> None:
    constraint_set = ConstraintSet()

    with pytest.raises(TypeError):
        constraint_set.add_constraint("invalid")  # type: ignore[arg-type]


def test_constraint_set_get_missing_constraint() -> None:
    constraint_set = ConstraintSet()

    assert constraint_set.get_constraint("missing") is None


def test_constraint_set_rejects_invalid_get_name() -> None:
    constraint_set = ConstraintSet()

    with pytest.raises(TypeError):
        constraint_set.get_constraint(123)  # type: ignore[arg-type]


def test_constraint_set_is_satisfied_when_empty() -> None:
    constraint_set = ConstraintSet()

    assert constraint_set.is_satisfied({}) is True


def test_constraint_set_is_satisfied_when_all_match() -> None:
    constraint_set = ConstraintSet(
        [
            Constraint("budget", 1000),
            Constraint("deadline", "2026-12-31"),
        ]
    )

    context = {
        "budget": 1000,
        "deadline": "2026-12-31",
    }

    assert constraint_set.is_satisfied(context) is True


def test_constraint_set_is_not_satisfied_when_one_constraint_fails() -> None:
    constraint_set = ConstraintSet(
        [
            Constraint("budget", 1000),
            Constraint("deadline", "2026-12-31"),
        ]
    )

    context = {
        "budget": 1000,
        "deadline": "2026-11-30",
    }

    assert constraint_set.is_satisfied(context) is False


def test_constraint_set_is_not_satisfied_when_constraint_missing() -> None:
    constraint_set = ConstraintSet(
        [
            Constraint("budget", 1000),
            Constraint("deadline", "2026-12-31"),
        ]
    )

    context = {
        "budget": 1000,
    }

    assert constraint_set.is_satisfied(context) is False


def test_constraint_set_rejects_invalid_context() -> None:
    constraint_set = ConstraintSet()

    with pytest.raises(TypeError):
        constraint_set.is_satisfied(None)  # type: ignore[arg-type]


def test_constraint_set_rejects_invalid_initial_constraints() -> None:
    with pytest.raises(TypeError):
        ConstraintSet("invalid")  # type: ignore[arg-type]


def test_constraint_set_rejects_invalid_initial_constraint_items() -> None:
    with pytest.raises(TypeError):
        ConstraintSet(
            [
                Constraint("budget", 1000),
                "invalid",  # type: ignore[list-item]
            ]
        )


def test_constraint_set_to_dict() -> None:
    constraint_set = ConstraintSet(
        [
            Constraint("budget", 1000),
            Constraint(
                "deadline",
                "2026-12-31",
                constraint_type="temporal",
            ),
        ]
    )

    assert constraint_set.to_dict() == {
        "budget": {
            "name": "budget",
            "value": 1000,
            "constraint_type": "generic",
        },
        "deadline": {
            "name": "deadline",
            "value": "2026-12-31",
            "constraint_type": "temporal",
        },
    }


def test_constraint_set_repr() -> None:
    constraint_set = ConstraintSet(
        [
            Constraint("budget", 1000),
            Constraint("deadline", "2026-12-31"),
        ]
    )

    result = repr(constraint_set)

    assert "ConstraintSet" in result
    assert "size=2" in result


def test_constraint_set_has_no_execution_state() -> None:
    constraint_set = ConstraintSet()

    for attribute in (
        "status",
        "result",
        "started_at",
        "completed_at",
        "error",
    ):
        assert not hasattr(constraint_set, attribute)