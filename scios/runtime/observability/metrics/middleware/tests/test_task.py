"""
Tests for SciOS Runtime Metrics Middleware Task.
"""

from __future__ import annotations

import pytest

from ..task import MetricMiddlewareTask


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def task() -> MetricMiddlewareTask:
    return MetricMiddlewareTask(
        name="test",
    )


# ============================================================================
# Construction
# ============================================================================


def test_default_construction(task):
    assert task.name == "test"
    assert task.description == ""
    assert task.priority == 0
    assert task.handler() is None

    assert task.enabled is True
    assert task.running is False
    assert task.completed is False
    assert task.failed is False
    assert task.cancelled is False
    assert task.active is True

    assert task.result is None
    assert task.error is None


def test_custom_construction():
    handler = lambda metric: metric

    task = MetricMiddlewareTask(
        name="custom",
        handler=handler,
        priority=10,
        description="test task",
    )

    assert task.name == "custom"
    assert task.description == "test task"
    assert task.priority == 10
    assert task.handler() is handler


def test_id_is_string(task):
    assert isinstance(task.id, str)
    assert task.id


def test_ids_are_unique():
    first = MetricMiddlewareTask("first")
    second = MetricMiddlewareTask("second")

    assert first.id != second.id


def test_name_requires_non_empty_string():
    with pytest.raises(ValueError):
        MetricMiddlewareTask("")


def test_name_requires_string():
    with pytest.raises(ValueError):
        MetricMiddlewareTask(None)


def test_handler_requires_callable():
    with pytest.raises(TypeError):
        MetricMiddlewareTask(
            "test",
            handler="invalid",
        )


def test_priority_requires_integer():
    with pytest.raises(TypeError):
        MetricMiddlewareTask(
            "test",
            priority="high",
        )


# ============================================================================
# Execution
# ============================================================================


def test_execute_without_handler_passes_metric_through(task):
    metric = {
        "name": "requests",
        "value": 10,
    }

    result = task.execute(metric)

    assert result == metric
    assert result is metric

    assert task.completed is True
    assert task.failed is False
    assert task.running is False


def test_execute_with_handler():
    task = MetricMiddlewareTask(
        "test",
        handler=lambda metric: {
            **metric,
            "processed": True,
        },
    )

    result = task.execute(
        {"name": "requests"}
    )

    assert result == {
        "name": "requests",
        "processed": True,
    }

    assert task.completed is True
    assert task.failed is False


def test_execute_passes_kwargs():
    def handler(metric, multiplier=1):
        return metric["value"] * multiplier

    task = MetricMiddlewareTask(
        "test",
        handler=handler,
    )

    assert task.execute(
        {"value": 10},
        multiplier=3,
    ) == 30


def test_run_is_alias(task):
    metric = {"value": 10}

    assert task.run(metric) == metric


def test_process_is_alias(task):
    metric = {"value": 10}

    assert task.process(metric) == metric


def test_call_is_alias(task):
    metric = {"value": 10}

    assert task(metric) == metric


# ============================================================================
# Execution Failure
# ============================================================================


def test_execution_failure():
    def handler(metric):
        raise RuntimeError("boom")

    task = MetricMiddlewareTask(
        "test",
        handler=handler,
    )

    with pytest.raises(RuntimeError, match="boom"):
        task.execute({})

    assert task.running is False
    assert task.completed is False
    assert task.failed is True
    assert task.error is not None
    assert isinstance(task.error, RuntimeError)


def test_failure_statistics():
    task = MetricMiddlewareTask(
        "test",
        handler=lambda metric: 1 / 0,
    )

    with pytest.raises(ZeroDivisionError):
        task.execute({})

    stats = task.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1


def test_success_clears_previous_error():
    calls = {"count": 0}

    def handler(metric):
        calls["count"] += 1

        if calls["count"] == 1:
            raise RuntimeError("boom")

        return metric

    task = MetricMiddlewareTask(
        "test",
        handler=handler,
    )

    with pytest.raises(RuntimeError):
        task.execute({})

    assert task.failed is True
    assert task.error is not None

    task.execute({"value": 1})

    assert task.completed is True
    assert task.failed is False
    assert task.error is None


# ============================================================================
# Handler Management
# ============================================================================


def test_set_handler(task):
    handler = lambda metric: metric["value"]

    assert task.set_handler(handler) is task
    assert task.handler() is handler


def test_set_handler_requires_callable(task):
    with pytest.raises(TypeError):
        task.set_handler("invalid")


def test_clear_handler(task):
    task.set_handler(
        lambda metric: metric
    )

    assert task.clear_handler() is task
    assert task.handler() is None


def test_handler_replacement():
    task = MetricMiddlewareTask(
        "test",
        handler=lambda metric: 1,
    )

    task.set_handler(
        lambda metric: 2
    )

    assert task.execute({}) == 2


# ============================================================================
# Cancellation
# ============================================================================


def test_cancel(task):
    assert task.cancel() is task

    assert task.cancelled is True
    assert task.running is False
    assert task.active is False


def test_cancelled_task_cannot_execute(task):
    task.cancel()

    with pytest.raises(
        RuntimeError,
        match="Task test cancelled",
    ):
        task.execute({})

    assert task.statistics()["executions"] == 0


def test_cancel_does_not_change_statistics(task):
    task.execute({"value": 1})

    task.cancel()

    stats = task.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


# ============================================================================
# Lifecycle
# ============================================================================


def test_disable(task):
    assert task.disable() is task

    assert task.enabled is False
    assert task.active is False


def test_disabled_task_cannot_execute(task):
    task.disable()

    with pytest.raises(
        RuntimeError,
        match="Task test disabled",
    ):
        task.execute({})

    assert task.statistics()["executions"] == 0


def test_enable(task):
    task.disable()

    assert task.enable() is task

    assert task.enabled is True
    assert task.active is True


def test_enable_does_not_clear_cancelled_state(task):
    task.cancel()

    task.enable()

    assert task.enabled is True
    assert task.cancelled is True
    assert task.active is False


# ============================================================================
# Reset
# ============================================================================


def test_reset_after_success(task):
    task.execute({"value": 1})

    assert task.completed is True
    assert task.result == {"value": 1}

    assert task.reset() is task

    assert task.running is False
    assert task.completed is False
    assert task.failed is False
    assert task.cancelled is False
    assert task.result is None
    assert task.error is None


def test_reset_after_failure():
    task = MetricMiddlewareTask(
        "test",
        handler=lambda metric: 1 / 0,
    )

    with pytest.raises(ZeroDivisionError):
        task.execute({})

    assert task.failed is True

    task.reset()

    assert task.failed is False
    assert task.completed is False
    assert task.error is None
    assert task.result is None
    assert task.cancelled is False


def test_reset_clears_cancelled_state(task):
    task.cancel()

    assert task.cancelled is True

    task.reset()

    assert task.cancelled is False
    assert task.active is True


def test_reset_preserves_statistics(task):
    task.execute({"value": 1})

    task.reset()

    stats = task.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_reset_preserves_configuration():
    handler = lambda metric: metric

    task = MetricMiddlewareTask(
        "custom",
        handler=handler,
        priority=5,
        description="description",
    )

    task.reset()

    assert task.name == "custom"
    assert task.description == "description"
    assert task.priority == 5
    assert task.handler() is handler


# ============================================================================
# Statistics
# ============================================================================


def test_success_statistics(task):
    task.execute({"value": 1})
    task.execute({"value": 2})

    stats = task.statistics()

    assert stats["executions"] == 2
    assert stats["success"] == 2
    assert stats["failures"] == 0
    assert stats["priority"] == 0


def test_priority_statistics():
    task = MetricMiddlewareTask(
        "test",
        priority=25,
    )

    assert task.statistics()["priority"] == 25


# ============================================================================
# Status
# ============================================================================


def test_status_initial(task):
    assert task.status() == {
        "enabled": True,
        "running": False,
        "completed": False,
        "failed": False,
        "cancelled": False,
        "active": True,
    }


def test_status_disabled(task):
    task.disable()

    assert task.status() == {
        "enabled": False,
        "running": False,
        "completed": False,
        "failed": False,
        "cancelled": False,
        "active": False,
    }


def test_status_cancelled(task):
    task.cancel()

    assert task.status() == {
        "enabled": True,
        "running": False,
        "completed": False,
        "failed": False,
        "cancelled": True,
        "active": False,
    }


# ============================================================================
# Representation
# ============================================================================


def test_repr(task):
    text = repr(task)

    assert text.startswith(
        "MetricMiddlewareTask("
    )
    assert "name='test'" in text
    assert "priority=0" in text
    assert "executions=0" in text


def test_str(task):
    assert str(task) == "test"