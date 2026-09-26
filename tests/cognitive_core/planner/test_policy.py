"""
Contract tests for SciOS Cognitive Core PlanningPolicy.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.planner.policy import PlanningPolicy
from scios.cognitive_core.planner.task import Task


class TestPlanningPolicyConstruction:
    def test_default_rules(self):
        policy = PlanningPolicy()

        assert policy.rules == {}

    def test_custom_rules_are_copied(self):
        rules = {"priority": 5}

        policy = PlanningPolicy(rules)

        assert policy.rules == rules
        assert policy.rules is not rules

    def test_rules_must_be_dictionary(self):
        with pytest.raises(TypeError):
            PlanningPolicy(rules=["priority"])

    def test_repr(self):
        policy = PlanningPolicy({"priority": 5})

        result = repr(policy)

        assert "PlanningPolicy" in result
        assert "priority" in result


class TestPlanningPolicyApply:
    def test_empty_tasks(self):
        policy = PlanningPolicy()

        assert policy.apply([]) == []

    def test_returns_list(self):
        policy = PlanningPolicy()
        task = Task("Task A", task_id="a")

        result = policy.apply([task])

        assert isinstance(result, list)
        assert result == [task]

    def test_preserves_task_objects(self):
        policy = PlanningPolicy()
        task_a = Task("Task A", task_id="a")
        task_b = Task("Task B", task_id="b")

        result = policy.apply([task_a, task_b])

        assert result[0] is task_a
        assert result[1] is task_b

    def test_does_not_mutate_input_list(self):
        policy = PlanningPolicy()
        task_a = Task("Task A", task_id="a")
        task_b = Task("Task B", task_id="b")
        tasks = [task_a, task_b]

        policy.apply(tasks)

        assert tasks == [task_a, task_b]

    def test_requires_iterable(self):
        policy = PlanningPolicy()

        with pytest.raises(TypeError):
            policy.apply(None)

    def test_rejects_string_input(self):
        policy = PlanningPolicy()

        with pytest.raises(TypeError):
            policy.apply("not-a-task-list")

    def test_rejects_non_task_items(self):
        policy = PlanningPolicy()

        with pytest.raises(TypeError):
            policy.apply([Task("Valid"), "invalid"])

    def test_orders_independent_tasks_by_priority(self):
        policy = PlanningPolicy()

        low = Task("Low", task_id="low")
        low.add_constraint("priority", 1)

        high = Task("High", task_id="high")
        high.add_constraint("priority", 10)

        result = policy.apply([low, high])

        assert [task.id for task in result] == [
            "high",
            "low",
        ]

    def test_equal_priority_preserves_input_order(self):
        policy = PlanningPolicy()

        first = Task("First", task_id="first")
        first.add_constraint("priority", 5)

        second = Task("Second", task_id="second")
        second.add_constraint("priority", 5)

        result = policy.apply([first, second])

        assert [task.id for task in result] == [
            "first",
            "second",
        ]

    def test_missing_priority_defaults_to_zero(self):
        policy = PlanningPolicy()

        task = Task("Task A", task_id="a")

        result = policy.apply([task])

        assert result == [task]

    def test_policy_priority_rule_provides_default(self):
        policy = PlanningPolicy({"priority": 10})

        task_a = Task("Task A", task_id="a")
        task_b = Task("Task B", task_id="b")
        task_b.add_constraint("priority", 20)

        result = policy.apply([task_a, task_b])

        assert [task.id for task in result] == [
            "b",
            "a",
        ]

    def test_task_priority_overrides_policy_default(self):
        policy = PlanningPolicy({"priority": 100})

        task_a = Task("Task A", task_id="a")
        task_a.add_constraint("priority", 1)

        task_b = Task("Task B", task_id="b")
        task_b.add_constraint("priority", 2)

        result = policy.apply([task_a, task_b])

        assert [task.id for task in result] == [
            "b",
            "a",
        ]

    def test_dependency_precedes_dependent(self):
        policy = PlanningPolicy()

        dependency = Task("Dependency", task_id="a")
        dependency.add_constraint("priority", 1)

        dependent = Task(
            "Dependent",
            task_id="b",
            dependencies=["a"],
        )
        dependent.add_constraint("priority", 100)

        result = policy.apply([dependent, dependency])

        assert [task.id for task in result] == [
            "a",
            "b",
        ]

    def test_dependency_chain_is_ordered_correctly(self):
        policy = PlanningPolicy()

        task_a = Task("A", task_id="a")
        task_b = Task(
            "B",
            task_id="b",
            dependencies=["a"],
        )
        task_c = Task(
            "C",
            task_id="c",
            dependencies=["b"],
        )

        result = policy.apply([task_c, task_b, task_a])

        assert [task.id for task in result] == [
            "a",
            "b",
            "c",
        ]

    def test_priority_applies_only_among_ready_tasks(self):
        policy = PlanningPolicy()

        dependency = Task("Dependency", task_id="a")
        dependency.add_constraint("priority", 1)

        dependent = Task(
            "Dependent",
            task_id="b",
            dependencies=["a"],
        )
        dependent.add_constraint("priority", 100)

        independent = Task("Independent", task_id="c")
        independent.add_constraint("priority", 50)

        result = policy.apply(
            [dependent, independent, dependency]
        )

        assert [task.id for task in result] == [
            "c",
            "a",
            "b",
        ]

    def test_multiple_ready_tasks_are_priority_ordered(self):
        policy = PlanningPolicy()

        task_a = Task("A", task_id="a")
        task_a.add_constraint("priority", 1)

        task_b = Task("B", task_id="b")
        task_b.add_constraint("priority", 10)

        task_c = Task("C", task_id="c")
        task_c.add_constraint("priority", 5)

        result = policy.apply([task_a, task_b, task_c])

        assert [task.id for task in result] == [
            "b",
            "c",
            "a",
        ]

    def test_unresolved_dependency_is_rejected(self):
        policy = PlanningPolicy()

        task = Task(
            "Task B",
            task_id="b",
            dependencies=["missing"],
        )

        with pytest.raises(
            ValueError,
            match="Unresolved dependency",
        ):
            policy.apply([task])

    def test_duplicate_task_ids_are_rejected(self):
        policy = PlanningPolicy()

        first = Task("First", task_id="same")
        second = Task("Second", task_id="same")

        with pytest.raises(
            ValueError,
            match="Duplicate task ID",
        ):
            policy.apply([first, second])

    def test_self_dependency_is_rejected(self):
        policy = PlanningPolicy()

        task = Task(
            "Task A",
            task_id="a",
            dependencies=["a"],
        )

        with pytest.raises(ValueError):
            policy.apply([task])

    def test_cycle_is_rejected(self):
        policy = PlanningPolicy()

        task_a = Task(
            "A",
            task_id="a",
            dependencies=["b"],
        )
        task_b = Task(
            "B",
            task_id="b",
            dependencies=["a"],
        )

        with pytest.raises(
            ValueError,
            match="cycle",
        ):
            policy.apply([task_a, task_b])

    def test_three_node_cycle_is_rejected(self):
        policy = PlanningPolicy()

        task_a = Task(
            "A",
            task_id="a",
            dependencies=["c"],
        )
        task_b = Task(
            "B",
            task_id="b",
            dependencies=["a"],
        )
        task_c = Task(
            "C",
            task_id="c",
            dependencies=["b"],
        )

        with pytest.raises(ValueError, match="cycle"):
            policy.apply([task_a, task_b, task_c])

    def test_priority_must_be_numeric(self):
        policy = PlanningPolicy()

        task = Task("Task A", task_id="a")
        task.add_constraint("priority", "high")

        with pytest.raises(TypeError, match="Priority"):
            policy.apply([task])

    def test_tasks_without_ids_are_allowed(self):
        policy = PlanningPolicy()

        task = Task("Task A")

        result = policy.apply([task])

        assert result == [task]
        assert task.id is None

    def test_unresolved_dependency_to_idless_task_is_rejected(self):
        policy = PlanningPolicy()

        dependency = Task("Dependency")
        dependent = Task(
            "Dependent",
            task_id="b",
            dependencies=["task-0"],
        )

        with pytest.raises(
            ValueError,
            match="Unresolved dependency",
        ):
            policy.apply([dependency, dependent])


class TestPlanningPolicyContract:
    def test_has_apply_method(self):
        assert hasattr(PlanningPolicy, "apply")

    def test_apply_returns_task_list(self):
        policy = PlanningPolicy()

        task = Task("Task A", task_id="a")

        result = policy.apply([task])

        assert isinstance(result, list)
        assert all(isinstance(item, Task) for item in result)

    def test_no_execution_state_is_created(self):
        policy = PlanningPolicy()

        task = Task("Task A", task_id="a")

        result = policy.apply([task])

        for item in result:
            assert not hasattr(item, "status")
            assert not hasattr(item, "result")
            assert not hasattr(item, "started_at")
            assert not hasattr(item, "completed_at")
            assert not hasattr(item, "error")
            assert not hasattr(item, "retry_count")

    def test_policy_does_not_execute_tasks(self):
        policy = PlanningPolicy()

        called = []

        class CallableTask:
            def __call__(self):
                called.append(True)

        task = Task("Task A", task_id="a")
        task.metadata["callable"] = CallableTask()

        policy.apply([task])

        assert called == []