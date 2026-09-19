"""
Tests for SciOS Runtime Metrics Middleware.
"""

from __future__ import annotations

import pytest

from ..middleware import MetricMiddleware


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def middleware() -> MetricMiddleware:

    return MetricMiddleware()


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(middleware):

    assert middleware.name == "MetricMiddleware"
    assert middleware.description == ""
    assert middleware.handler() is None
    assert middleware.enabled is True
    assert middleware.running is False
    assert middleware.closed is False


def test_custom_construction():

    middleware = MetricMiddleware(
        name="custom",
        description="test",
    )

    assert middleware.name == "custom"
    assert middleware.description == "test"


def test_unique_ids():

    first = MetricMiddleware()
    second = MetricMiddleware()

    assert first.id != second.id


# ==============================================================
# Pass-through
# ==============================================================


def test_execute_without_handler(middleware):

    metric = {
        "name": "requests",
        "value": 10,
    }

    result = middleware.execute(metric)

    assert result is metric
    assert result == metric


def test_run_is_alias(middleware):

    metric = {
        "name": "requests",
    }

    assert middleware.run(metric) is metric


def test_process_is_alias(middleware):

    metric = {
        "name": "requests",
    }

    assert middleware.process(metric) is metric


# ==============================================================
# Handler
# ==============================================================


def test_handler_execution():

    middleware = MetricMiddleware(
        handler=lambda metric: {
            **metric,
            "processed": True,
        }
    )

    result = middleware.execute(
        {"name": "requests"}
    )

    assert result == {
        "name": "requests",
        "processed": True,
    }


def test_handler_receives_kwargs():

    middleware = MetricMiddleware(
        handler=lambda metric, **kwargs: {
            **metric,
            **kwargs,
        }
    )

    result = middleware.execute(
        {"name": "requests"},
        source="runtime",
    )

    assert result["source"] == "runtime"


def test_set_handler(middleware):

    handler = lambda metric: metric

    assert middleware.set_handler(
        handler
    ) is middleware

    assert middleware.handler() is handler


def test_set_handler_requires_callable(middleware):

    with pytest.raises(TypeError):

        middleware.set_handler(
            "invalid"
        )


def test_clear_handler(middleware):

    middleware.set_handler(
        lambda metric: "changed"
    )

    assert middleware.clear_handler() is middleware
    assert middleware.handler() is None

    metric = {"name": "requests"}

    assert middleware.execute(metric) is metric


# ==============================================================
# Statistics
# ==============================================================


def test_success_statistics(middleware):

    middleware.execute(
        {"name": "requests"}
    )

    stats = middleware.statistics()

    assert stats["name"] == "MetricMiddleware"
    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_multiple_executions(middleware):

    middleware.execute({})
    middleware.execute({})
    middleware.execute({})

    stats = middleware.statistics()

    assert stats["executions"] == 3
    assert stats["success"] == 3
    assert stats["failures"] == 0


def test_failure_statistics():

    def handler(metric):

        raise RuntimeError("boom")

    middleware = MetricMiddleware(
        handler=handler
    )

    with pytest.raises(RuntimeError):

        middleware.execute({})

    stats = middleware.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1


def test_last_result():

    middleware = MetricMiddleware(
        handler=lambda metric: {
            "value": 42
        }
    )

    result = middleware.execute({})

    assert middleware.last_result == result


def test_last_error():

    error = RuntimeError("boom")

    def handler(metric):

        raise error

    middleware = MetricMiddleware(
        handler=handler
    )

    with pytest.raises(RuntimeError):

        middleware.execute({})

    assert middleware.last_error is error


# ==============================================================
# Lifecycle
# ==============================================================


def test_disable(middleware):

    assert middleware.disable() is middleware
    assert middleware.enabled is False

    with pytest.raises(RuntimeError):

        middleware.execute({})


def test_enable(middleware):

    middleware.disable()

    assert middleware.enable() is middleware
    assert middleware.enabled is True

    assert middleware.execute({}) == {}


def test_close(middleware):

    assert middleware.close() is middleware
    assert middleware.closed is True

    with pytest.raises(RuntimeError):

        middleware.execute({})


def test_reopen(middleware):

    middleware.close()

    assert middleware.reopen() is middleware
    assert middleware.closed is False

    assert middleware.execute({}) == {}


def test_disable_error_message(middleware):

    middleware.disable()

    with pytest.raises(
        RuntimeError,
        match="Middleware MetricMiddleware disabled",
    ):

        middleware.execute({})


def test_close_error_message(middleware):

    middleware.close()

    with pytest.raises(
        RuntimeError,
        match="Middleware MetricMiddleware closed",
    ):

        middleware.execute({})


# ==============================================================
# Status
# ==============================================================


def test_status_default(middleware):

    assert middleware.status() == {
        "enabled": True,
        "running": False,
        "closed": False,
        "active": True,
    }


def test_status_disabled(middleware):

    middleware.disable()

    assert middleware.status() == {
        "enabled": False,
        "running": False,
        "closed": False,
        "active": False,
    }


def test_status_closed(middleware):

    middleware.close()

    assert middleware.status() == {
        "enabled": True,
        "running": False,
        "closed": True,
        "active": False,
    }


# ==============================================================
# Reset
# ==============================================================


def test_reset():

    middleware = MetricMiddleware(
        handler=lambda metric: {
            "value": 42
        }
    )

    middleware.execute({})

    assert middleware.statistics()["executions"] == 1
    assert middleware.last_result == {
        "value": 42
    }

    assert middleware.reset() is middleware

    stats = middleware.statistics()

    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0

    assert middleware.last_result is None
    assert middleware.last_error is None

    # Configuration survives reset.
    assert middleware.handler() is not None
    assert middleware.enabled is True
    assert middleware.closed is False


# ==============================================================
# Python Protocols
# ==============================================================


def test_call():

    middleware = MetricMiddleware(
        handler=lambda metric: {
            **metric,
            "processed": True,
        }
    )

    result = middleware(
        {"name": "requests"}
    )

    assert result == {
        "name": "requests",
        "processed": True,
    }


def test_repr(middleware):

    text = repr(middleware)

    assert text.startswith(
        "MetricMiddleware("
    )

    assert "executions=0" in text


def test_str(middleware):

    assert str(middleware) == "MetricMiddleware"


# ==============================================================
# Regression
# ==============================================================


def test_failed_execution_does_not_increment_success():

    middleware = MetricMiddleware(
        handler=lambda metric: 1 / 0
    )

    with pytest.raises(
        ZeroDivisionError
    ):

        middleware.execute({})

    stats = middleware.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1
