"""
Tests for SciOS Runtime Metrics Middleware Integration.
"""

from __future__ import annotations

import pytest

from ..middleware_integration import MetricMiddlewareIntegration


# ==============================================================
# Test Middleware Implementations
# ==============================================================


class ExecuteMiddleware:
    def __init__(self, suffix: str = ""):
        self.suffix = suffix

    def execute(self, metric, **kwargs):
        result = dict(metric)
        result["value"] = (
            result.get("value", "")
            + self.suffix
        )
        return result


class ProcessMiddleware:
    def process(self, metric, **kwargs):
        return {
            **metric,
            "processed": True,
        }


class RunMiddleware:
    def run(self, metric, **kwargs):
        return {
            **metric,
            "ran": True,
        }


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def integration():
    return MetricMiddlewareIntegration()


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(integration):
    assert integration.name == (
        "MetricMiddlewareIntegration"
    )
    assert integration.description == ""
    assert integration.middlewares_count == 0
    assert len(integration) == 0


def test_custom_construction():
    middleware = ExecuteMiddleware()

    integration = MetricMiddlewareIntegration(
        middlewares=[middleware],
        name="custom",
        description="test",
    )

    assert integration.name == "custom"
    assert integration.description == "test"
    assert integration.middlewares_count == 1


# ==============================================================
# Management
# ==============================================================


def test_add_middleware(integration):
    middleware = ExecuteMiddleware()

    assert integration.add_middleware(
        middleware
    ) is integration

    assert len(integration) == 1
    assert middleware in integration


def test_add_none_requires_value(integration):
    with pytest.raises(ValueError):
        integration.add_middleware(None)


def test_add_invalid_middleware_requires_api(integration):
    with pytest.raises(TypeError):
        integration.add_middleware(object())


def test_remove_middleware(integration):
    middleware = ExecuteMiddleware()

    integration.add_middleware(middleware)

    assert integration.remove_middleware(
        middleware
    ) is integration

    assert len(integration) == 0


def test_remove_missing_middleware_is_safe(integration):
    middleware = ExecuteMiddleware()

    assert integration.remove_middleware(
        middleware
    ) is integration


def test_clear_middlewares(integration):
    integration.add_middleware(
        ExecuteMiddleware()
    )
    integration.add_middleware(
        ProcessMiddleware()
    )

    assert integration.clear_middlewares() is integration
    assert integration.middlewares() == []


def test_middlewares_returns_copy(integration):
    middleware = ExecuteMiddleware()

    integration.add_middleware(middleware)

    middlewares = integration.middlewares()
    middlewares.clear()

    assert len(integration) == 1


def test_get_middleware(integration):
    first = ExecuteMiddleware("-a")
    second = ProcessMiddleware()

    integration.add_middleware(first)
    integration.add_middleware(second)

    assert integration.get_middleware(0) is first
    assert integration.get_middleware(1) is second


# ==============================================================
# Execution
# ==============================================================


def test_execute_empty_chain(integration):
    metric = {
        "name": "requests",
        "value": 10,
    }

    result = integration.execute(metric)

    assert result == metric
    assert result is metric


def test_execute_execute_middleware(integration):
    integration.add_middleware(
        ExecuteMiddleware("-a")
    )

    result = integration.execute(
        {"value": "base"}
    )

    assert result == {
        "value": "base-a"
    }


def test_execute_process_middleware(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    result = integration.execute({})

    assert result["processed"] is True


def test_execute_run_middleware(integration):
    integration.add_middleware(
        RunMiddleware()
    )

    result = integration.execute({})

    assert result["ran"] is True


def test_execute_callable_middleware(integration):
    integration.add_middleware(
        lambda metric: {
            **metric,
            "called": True,
        }
    )

    result = integration.execute({})

    assert result["called"] is True


def test_execute_preserves_order(integration):
    integration.add_middleware(
        ExecuteMiddleware("-a")
    )
    integration.add_middleware(
        ExecuteMiddleware("-b")
    )

    result = integration.execute(
        {"value": "base"}
    )

    assert result == {
        "value": "base-a-b"
    }


def test_execute_passes_kwargs(integration):
    class Middleware:
        def execute(self, metric, **kwargs):
            return {
                **metric,
                "source": kwargs["source"],
            }

    integration.add_middleware(Middleware())

    result = integration.execute(
        {},
        source="runtime",
    )

    assert result["source"] == "runtime"


# ==============================================================
# Aliases
# ==============================================================


def test_process_alias(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    assert integration.process({}) == {
        "processed": True
    }


def test_run_alias(integration):
    integration.add_middleware(
        RunMiddleware()
    )

    assert integration.run({}) == {
        "ran": True
    }


def test_call_alias(integration):
    integration.add_middleware(
        lambda metric: {
            **metric,
            "called": True,
        }
    )

    assert integration({}) == {
        "called": True
    }


# ==============================================================
# Batch Execution
# ==============================================================


def test_execute_many(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    result = integration.execute_many(
        [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ]
    )

    assert result == [
        {"id": 1, "processed": True},
        {"id": 2, "processed": True},
        {"id": 3, "processed": True},
    ]


def test_process_many(integration):
    integration.add_middleware(
        RunMiddleware()
    )

    result = integration.process_many(
        [
            {"id": 1},
            {"id": 2},
        ]
    )

    assert result == [
        {"id": 1, "ran": True},
        {"id": 2, "ran": True},
    ]


# ==============================================================
# Validation
# ==============================================================


def test_validate_empty_chain(integration):
    assert integration.validate_chain() is True


def test_validate_chain(integration):
    integration.add_middleware(
        ExecuteMiddleware()
    )
    integration.add_middleware(
        ProcessMiddleware()
    )

    assert integration.validate_chain() is True


# ==============================================================
# Error Handling
# ==============================================================


def test_execution_error_is_recorded(integration):
    def failing(metric):
        raise RuntimeError("boom")

    integration.add_middleware(failing)

    with pytest.raises(RuntimeError, match="boom"):
        integration.execute({})

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1

    assert isinstance(
        integration.last_error,
        RuntimeError,
    )


def test_failed_execution_clears_last_result(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    integration.execute({})

    assert integration.last_result is not None

    integration.clear_middlewares()

    def failing(metric):
        raise RuntimeError("boom")

    integration.add_middleware(failing)

    with pytest.raises(RuntimeError):
        integration.execute({})

    assert integration.last_result is None


# ==============================================================
# Statistics
# ==============================================================


def test_statistics(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    integration.execute({})

    stats = integration.statistics()

    assert stats["middlewares"] == 1
    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_statistics_multiple_executions(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    integration.execute({})
    integration.execute({})

    stats = integration.statistics()

    assert stats["executions"] == 2
    assert stats["success"] == 2
    assert stats["failures"] == 0


# ==============================================================
# Status
# ==============================================================


def test_status_empty(integration):
    status = integration.status()

    assert status["middlewares"] == 0
    assert status["active"] is False
    assert status["valid"] is True


def test_status_with_middlewares(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    status = integration.status()

    assert status["middlewares"] == 1
    assert status["active"] is True
    assert status["valid"] is True


# ==============================================================
# Reset
# ==============================================================


def test_reset_preserves_configuration(integration):
    integration.add_middleware(
        ProcessMiddleware()
    )

    integration.execute({})

    assert integration.statistics()["executions"] == 1

    assert integration.reset() is integration

    stats = integration.statistics()

    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0

    assert len(integration) == 1


# ==============================================================
# Protocols
# ==============================================================


def test_iteration(integration):
    first = ExecuteMiddleware("-a")
    second = ProcessMiddleware()

    integration.add_middleware(first)
    integration.add_middleware(second)

    assert list(integration) == [
        first,
        second,
    ]


def test_contains(integration):
    middleware = ProcessMiddleware()

    integration.add_middleware(middleware)

    assert middleware in integration


def test_repr(integration):
    text = repr(integration)

    assert text.startswith(
        "MetricMiddlewareIntegration("
    )

    assert "middlewares=0" in text
    assert "executions=0" in text


def test_str(integration):
    assert str(integration) == (
        "MetricMiddlewareIntegration"
    )