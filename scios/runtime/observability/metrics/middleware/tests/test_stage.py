"""
Tests for SciOS Runtime Metrics Middleware Stage.
"""

from __future__ import annotations

import pytest

from ..stage import MetricMiddlewareStage


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def stage() -> MetricMiddlewareStage:
    return MetricMiddlewareStage(
        name="test",
    )


# ============================================================================
# Construction
# ============================================================================


def test_default_construction(stage):
    assert stage.name == "test"
    assert stage.description == ""
    assert stage.handler() is None
    assert stage.enabled is True
    assert stage.running is False
    assert stage.closed is False
    assert stage.active is True


def test_custom_construction():
    handler = lambda metric: metric

    stage = MetricMiddlewareStage(
        name="custom",
        handler=handler,
        description="test stage",
    )

    assert stage.name == "custom"
    assert stage.description == "test stage"
    assert stage.handler() is handler


def test_id_is_string(stage):
    assert isinstance(stage.id, str)
    assert stage.id


def test_name_requires_non_empty_string():
    with pytest.raises(ValueError):
        MetricMiddlewareStage("")


def test_name_requires_string():
    with pytest.raises(ValueError):
        MetricMiddlewareStage(None)


def test_handler_requires_callable():
    with pytest.raises(TypeError):
        MetricMiddlewareStage(
            "test",
            handler="invalid",
        )


# ============================================================================
# Execution
# ============================================================================


def test_execute_without_handler_passes_metric_through(stage):
    metric = {
        "name": "requests",
        "value": 10,
    }

    result = stage.execute(metric)

    assert result == metric
    assert result is metric


def test_execute_with_handler():
    stage = MetricMiddlewareStage(
        "test",
        handler=lambda metric: {
            **metric,
            "processed": True,
        },
    )

    result = stage.execute(
        {"name": "requests"}
    )

    assert result == {
        "name": "requests",
        "processed": True,
    }


def test_execute_passes_kwargs():
    def handler(metric, multiplier=1):
        return metric["value"] * multiplier

    stage = MetricMiddlewareStage(
        "test",
        handler=handler,
    )

    assert stage.execute(
        {"value": 10},
        multiplier=3,
    ) == 30


def test_run_is_alias(stage):
    metric = {"value": 10}

    assert stage.run(metric) == metric


def test_process_is_alias(stage):
    metric = {"value": 10}

    assert stage.process(metric) == metric


def test_call_is_alias(stage):
    metric = {"value": 10}

    assert stage(metric) == metric


# ============================================================================
# Handler Management
# ============================================================================


def test_set_handler(stage):
    handler = lambda metric: metric["value"]

    assert stage.set_handler(handler) is stage
    assert stage.handler() is handler


def test_set_handler_requires_callable(stage):
    with pytest.raises(TypeError):
        stage.set_handler("invalid")


def test_clear_handler(stage):
    stage.set_handler(
        lambda metric: metric
    )

    assert stage.clear_handler() is stage
    assert stage.handler() is None


def test_handler_replacement():
    stage = MetricMiddlewareStage(
        "test",
        handler=lambda metric: 1,
    )

    stage.set_handler(
        lambda metric: 2
    )

    assert stage.execute({}) == 2


# ============================================================================
# Statistics
# ============================================================================


def test_success_statistics(stage):
    stage.execute({"value": 1})
    stage.execute({"value": 2})

    stats = stage.statistics()

    assert stats["executions"] == 2
    assert stats["success"] == 2
    assert stats["failures"] == 0


def test_failure_statistics():
    def handler(metric):
        raise RuntimeError("boom")

    stage = MetricMiddlewareStage(
        "test",
        handler=handler,
    )

    with pytest.raises(RuntimeError, match="boom"):
        stage.execute({})

    stats = stage.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1
    assert isinstance(stats["last_error"], RuntimeError)


def test_success_clears_previous_error():
    calls = {"count": 0}

    def handler(metric):
        calls["count"] += 1

        if calls["count"] == 1:
            raise RuntimeError("boom")

        return metric

    stage = MetricMiddlewareStage(
        "test",
        handler=handler,
    )

    with pytest.raises(RuntimeError):
        stage.execute({})

    assert stage.statistics()["last_error"] is not None

    stage.execute({"value": 1})

    stats = stage.statistics()

    assert stats["executions"] == 2
    assert stats["success"] == 1
    assert stats["failures"] == 1
    assert stats["last_error"] is None


def test_last_result(stage):
    result = stage.execute(
        {"value": 42}
    )

    assert stage.statistics()["last_result"] == result


# ============================================================================
# Lifecycle
# ============================================================================


def test_disable(stage):
    assert stage.disable() is stage

    assert stage.enabled is False
    assert stage.active is False


def test_disabled_stage_cannot_execute(stage):
    stage.disable()

    with pytest.raises(
        RuntimeError,
        match="Stage test disabled",
    ):
        stage.execute({})

    assert stage.statistics()["executions"] == 0


def test_enable(stage):
    stage.disable()

    assert stage.enable() is stage

    assert stage.enabled is True
    assert stage.active is True


def test_close(stage):
    assert stage.close() is stage

    assert stage.closed is True
    assert stage.active is False


def test_closed_stage_cannot_execute(stage):
    stage.close()

    with pytest.raises(
        RuntimeError,
        match="Stage test closed",
    ):
        stage.execute({})

    assert stage.statistics()["executions"] == 0


def test_reopen(stage):
    stage.close()

    assert stage.reopen() is stage

    assert stage.closed is False
    assert stage.active is True


def test_disable_and_reopen_does_not_enable(stage):
    stage.disable()
    stage.close()

    stage.reopen()

    assert stage.enabled is False
    assert stage.closed is False
    assert stage.active is False


# ============================================================================
# Status
# ============================================================================


def test_status_active(stage):
    assert stage.status() == {
        "enabled": True,
        "running": False,
        "closed": False,
        "active": True,
    }


def test_status_disabled(stage):
    stage.disable()

    assert stage.status() == {
        "enabled": False,
        "running": False,
        "closed": False,
        "active": False,
    }


def test_status_closed(stage):
    stage.close()

    assert stage.status() == {
        "enabled": True,
        "running": False,
        "closed": True,
        "active": False,
    }


# ============================================================================
# Reset
# ============================================================================


def test_reset_statistics(stage):
    stage.execute({"value": 1})
    stage.execute({"value": 2})

    assert stage.statistics()["executions"] == 2

    assert stage.reset() is stage

    stats = stage.statistics()

    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0
    assert stats["last_result"] is None
    assert stats["last_error"] is None


def test_reset_preserves_configuration():
    handler = lambda metric: metric

    stage = MetricMiddlewareStage(
        "custom",
        handler=handler,
        description="description",
    )

    stage.execute({"value": 1})
    stage.reset()

    assert stage.name == "custom"
    assert stage.description == "description"
    assert stage.handler() is handler


def test_reset_preserves_lifecycle_state(stage):
    stage.disable()
    stage.close()

    stage.reset()

    assert stage.enabled is False
    assert stage.closed is True
    assert stage.active is False


# ============================================================================
# Protocols
# ============================================================================


def test_repr(stage):
    text = repr(stage)

    assert text.startswith(
        "MetricMiddlewareStage("
    )
    assert "name='test'" in text
    assert "executions=0" in text


def test_str(stage):
    assert str(stage) == "test"


# ============================================================================
# Identity
# ============================================================================


def test_stage_ids_are_unique():
    first = MetricMiddlewareStage("first")
    second = MetricMiddlewareStage("second")

    assert first.id != second.id