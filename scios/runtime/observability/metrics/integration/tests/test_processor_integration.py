"""
Tests for SciOS Runtime Metrics Processor Integration.
"""

from __future__ import annotations

import pytest

from ..processor_integration import MetricProcessorIntegration


# ==============================================================
# Fixtures
# ==============================================================


class TransformProcessor:
    def __init__(self, suffix: str):
        self.suffix = suffix

    def transform(self, metric, **kwargs):
        result = dict(metric)
        result["value"] = (
            result.get("value", "")
            + self.suffix
        )
        return result


class ProcessProcessor:
    def process(self, metric, **kwargs):
        result = dict(metric)
        result["processed"] = True
        return result


class ExecuteProcessor:
    def execute(self, metric, **kwargs):
        result = dict(metric)
        result["executed"] = True
        return result


@pytest.fixture
def integration():
    return MetricProcessorIntegration()


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(integration):
    assert integration.name == "MetricProcessorIntegration"
    assert integration.description == ""
    assert integration.processors_count == 0
    assert len(integration) == 0


def test_custom_construction():
    processor = TransformProcessor("-a")

    integration = MetricProcessorIntegration(
        processors=[processor],
        name="custom",
        description="test",
    )

    assert integration.name == "custom"
    assert integration.description == "test"
    assert integration.processors_count == 1


# ==============================================================
# Processor Management
# ==============================================================


def test_add_processor(integration):
    processor = TransformProcessor("-a")

    assert integration.add_processor(
        processor
    ) is integration

    assert len(integration) == 1
    assert processor in integration


def test_add_none_requires_value(integration):
    with pytest.raises(ValueError):
        integration.add_processor(None)


def test_add_invalid_processor_requires_api(integration):
    with pytest.raises(TypeError):
        integration.add_processor(
            object()
        )


def test_remove_processor(integration):
    processor = TransformProcessor("-a")

    integration.add_processor(processor)

    assert integration.remove_processor(
        processor
    ) is integration

    assert len(integration) == 0


def test_remove_missing_processor_is_safe(integration):
    processor = TransformProcessor("-a")

    assert integration.remove_processor(
        processor
    ) is integration


def test_clear_processors(integration):
    integration.add_processor(
        TransformProcessor("-a")
    )
    integration.add_processor(
        ProcessProcessor()
    )

    assert integration.clear_processors() is integration
    assert integration.processors() == []


def test_processors_returns_copy(integration):
    processor = TransformProcessor("-a")

    integration.add_processor(processor)

    processors = integration.processors()
    processors.clear()

    assert len(integration) == 1


def test_get_processor(integration):
    first = TransformProcessor("-a")
    second = ProcessProcessor()

    integration.add_processor(first)
    integration.add_processor(second)

    assert integration.get_processor(0) is first
    assert integration.get_processor(1) is second


# ==============================================================
# Chain Execution
# ==============================================================


def test_execute_empty_chain(integration):
    metric = {
        "name": "requests",
        "value": 10,
    }

    result = integration.execute(metric)

    assert result == metric
    assert result is metric


def test_execute_transform_processor(integration):
    integration.add_processor(
        TransformProcessor("-a")
    )

    result = integration.execute(
        {"value": "base"}
    )

    assert result == {
        "value": "base-a"
    }


def test_execute_process_processor(integration):
    integration.add_processor(
        ProcessProcessor()
    )

    result = integration.execute({})

    assert result["processed"] is True


def test_execute_execute_processor(integration):
    integration.add_processor(
        ExecuteProcessor()
    )

    result = integration.execute({})

    assert result["executed"] is True


def test_execute_callable_processor(integration):
    integration.add_processor(
        lambda metric: {
            **metric,
            "called": True,
        }
    )

    result = integration.execute({})

    assert result["called"] is True


def test_execute_preserves_order(integration):
    integration.add_processor(
        TransformProcessor("-a")
    )

    integration.add_processor(
        TransformProcessor("-b")
    )

    result = integration.execute(
        {"value": "base"}
    )

    assert result == {
        "value": "base-a-b"
    }


def test_execute_passes_kwargs(integration):
    class Processor:
        def transform(self, metric, **kwargs):
            return {
                **metric,
                "source": kwargs["source"],
            }

    integration.add_processor(
        Processor()
    )

    result = integration.execute(
        {},
        source="runtime",
    )

    assert result["source"] == "runtime"


# ==============================================================
# Aliases
# ==============================================================


def test_process_alias(integration):
    integration.add_processor(
        ProcessProcessor()
    )

    assert integration.process({}) == {
        "processed": True
    }


def test_run_alias(integration):
    integration.add_processor(
        ExecuteProcessor()
    )

    assert integration.run({}) == {
        "executed": True
    }


def test_call_alias(integration):
    integration.add_processor(
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
    integration.add_processor(
        ProcessProcessor()
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
    integration.add_processor(
        ExecuteProcessor()
    )

    result = integration.process_many(
        [
            {"id": 1},
            {"id": 2},
        ]
    )

    assert result == [
        {"id": 1, "executed": True},
        {"id": 2, "executed": True},
    ]


# ==============================================================
# Validation
# ==============================================================


def test_validate_empty_chain(integration):
    assert integration.validate_chain() is True


def test_validate_chain(integration):
    integration.add_processor(
        TransformProcessor("-a")
    )

    integration.add_processor(
        ProcessProcessor()
    )

    assert integration.validate_chain() is True


# ==============================================================
# Error Handling
# ==============================================================


def test_execution_error_is_recorded(integration):
    def failing(metric):
        raise RuntimeError("boom")

    integration.add_processor(failing)

    with pytest.raises(RuntimeError, match="boom"):
        integration.execute({})

    assert integration.statistics()["executions"] == 1
    assert integration.statistics()["success"] == 0
    assert integration.statistics()["failures"] == 1
    assert isinstance(
        integration.last_error,
        RuntimeError,
    )


def test_failed_execution_clears_last_result(integration):
    integration.add_processor(
        ProcessProcessor()
    )

    integration.execute({})

    assert integration.last_result is not None

    integration.clear_processors()

    def failing(metric):
        raise RuntimeError("boom")

    integration.add_processor(failing)

    with pytest.raises(RuntimeError):
        integration.execute({})

    assert integration.last_result is None


# ==============================================================
# Statistics
# ==============================================================


def test_statistics(integration):
    integration.add_processor(
        ProcessProcessor()
    )

    integration.execute({})

    stats = integration.statistics()

    assert stats["processors"] == 1
    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_statistics_multiple_executions(integration):
    integration.add_processor(
        ProcessProcessor()
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

    assert status["processors"] == 0
    assert status["active"] is False
    assert status["valid"] is True


def test_status_with_processors(integration):
    integration.add_processor(
        ProcessProcessor()
    )

    status = integration.status()

    assert status["processors"] == 1
    assert status["active"] is True
    assert status["valid"] is True


# ==============================================================
# Reset
# ==============================================================


def test_reset_preserves_configuration(integration):
    integration.add_processor(
        ProcessProcessor()
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
    first = TransformProcessor("-a")
    second = ProcessProcessor()

    integration.add_processor(first)
    integration.add_processor(second)

    assert list(integration) == [
        first,
        second,
    ]


def test_contains(integration):
    processor = ProcessProcessor()

    integration.add_processor(processor)

    assert processor in integration


def test_repr(integration):
    text = repr(integration)

    assert text.startswith(
        "MetricProcessorIntegration("
    )

    assert "processors=0" in text
    assert "executions=0" in text


def test_str(integration):
    assert str(integration) == (
        "MetricProcessorIntegration"
    )