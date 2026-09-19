"""
Tests for MetricQTCIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..qtc import MetricQTCIntegration


# ==============================================================
# Helpers
# ==============================================================


class EvaluateQTC:

    def __init__(self):
        self.calls = 0
        self.records = []

    def evaluate(self, metric, **kwargs):
        self.calls += 1

        return {
            **metric,
            "evaluated": True,
        }

    def record(self, key, value):
        self.records.append(
            (key, value)
        )


class ApplyQTC:

    def apply(self, metric, **kwargs):
        return {
            **metric,
            "applied": True,
        }


class ExecuteQTC:

    def execute(self, metric, **kwargs):
        return {
            **metric,
            "executed": True,
        }


class ProcessQTC:

    def process(self, metric, **kwargs):
        return {
            **metric,
            "processed": True,
        }


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():

    integration = MetricQTCIntegration()

    assert integration.name == "MetricQTCIntegration"
    assert integration.description == ""
    assert integration.qtc is None
    assert integration.configured is False
    assert integration.last_result is None
    assert integration.last_error is None


def test_constructor_qtc():

    qtc = EvaluateQTC()

    integration = MetricQTCIntegration(
        qtc=qtc,
    )

    assert integration.qtc is qtc
    assert integration.configured is True


# ==============================================================
# Management
# ==============================================================


def test_set_qtc():

    integration = MetricQTCIntegration()
    qtc = EvaluateQTC()

    assert integration.set_qtc(qtc) is integration
    assert integration.qtc is qtc
    assert integration.configured is True


def test_clear_qtc():

    integration = MetricQTCIntegration(
        qtc=EvaluateQTC(),
    )

    assert integration.clear_qtc() is integration

    assert integration.qtc is None
    assert integration.configured is False


# ==============================================================
# Validation
# ==============================================================


def test_validate_empty():

    integration = MetricQTCIntegration()

    assert integration.validate() is True


def test_validate_valid():

    integration = MetricQTCIntegration(
        qtc=EvaluateQTC(),
    )

    assert integration.validate() is True


def test_validate_invalid():

    integration = MetricQTCIntegration(
        qtc=object(),
    )

    assert integration.validate() is False


# ==============================================================
# Execution
# ==============================================================


def test_execute_without_qtc():

    integration = MetricQTCIntegration()

    metric = {
        "value": 42,
    }

    assert integration.execute(metric) == metric
    assert integration.last_result == metric

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_evaluate_qtc():

    qtc = EvaluateQTC()

    integration = MetricQTCIntegration(
        qtc=qtc,
    )

    result = integration.execute(
        {"value": 1},
    )

    assert result == {
        "value": 1,
        "evaluated": True,
    }

    assert qtc.calls == 1


def test_apply_qtc():

    integration = MetricQTCIntegration(
        qtc=ApplyQTC(),
    )

    result = integration.execute(
        {"value": 1},
    )

    assert result["applied"] is True


def test_execute_qtc():

    integration = MetricQTCIntegration(
        qtc=ExecuteQTC(),
    )

    result = integration.execute(
        {"value": 1},
    )

    assert result["executed"] is True


def test_process_qtc():

    integration = MetricQTCIntegration(
        qtc=ProcessQTC(),
    )

    result = integration.execute(
        {"value": 1},
    )

    assert result["processed"] is True


def test_callable_qtc():

    integration = MetricQTCIntegration(
        qtc=lambda metric, **kwargs: {
            **metric,
            "callable": True,
        },
    )

    result = integration.execute(
        {"value": 1},
    )

    assert result["callable"] is True


def test_invalid_qtc_execution():

    integration = MetricQTCIntegration(
        qtc=object(),
    )

    with pytest.raises(
        TypeError,
        match="supported execution API",
    ):
        integration.execute({})

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1


# ==============================================================
# Aliases
# ==============================================================


def test_evaluate_alias():

    integration = MetricQTCIntegration()

    result = integration.evaluate(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


def test_apply_alias():

    integration = MetricQTCIntegration()

    result = integration.apply(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


def test_process_alias():

    integration = MetricQTCIntegration()

    result = integration.process(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


def test_run_alias():

    integration = MetricQTCIntegration()

    result = integration.run(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


def test_call():

    integration = MetricQTCIntegration()

    result = integration(
        {"value": 1},
    )

    assert result == {
        "value": 1,
    }


# ==============================================================
# Batch
# ==============================================================


def test_execute_many():

    integration = MetricQTCIntegration()

    results = integration.execute_many(
        [
            {"value": 1},
            {"value": 2},
            {"value": 3},
        ]
    )

    assert len(results) == 3
    assert results[0]["value"] == 1
    assert results[1]["value"] == 2
    assert results[2]["value"] == 3

    assert integration.statistics()["executions"] == 3


def test_process_many():

    integration = MetricQTCIntegration()

    results = integration.process_many(
        [
            {"value": 1},
            {"value": 2},
        ]
    )

    assert len(results) == 2


# ==============================================================
# Metadata
# ==============================================================


def test_record_without_qtc():

    integration = MetricQTCIntegration()

    assert integration.record(
        "metric.value",
        42,
    ) is integration


def test_record():

    qtc = EvaluateQTC()

    integration = MetricQTCIntegration(
        qtc=qtc,
    )

    assert integration.record(
        "metric.value",
        42,
    ) is integration

    assert qtc.records == [
        (
            "metric.value",
            42,
        )
    ]


# ==============================================================
# Error Handling
# ==============================================================


def test_execution_failure():

    error = RuntimeError("boom")

    def failing(metric):
        raise error

    integration = MetricQTCIntegration(
        qtc=failing,
    )

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        integration.execute({})

    assert integration.last_error is error
    assert integration.last_result is None

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1


# ==============================================================
# Diagnostics
# ==============================================================


def test_statistics():

    integration = MetricQTCIntegration()

    stats = integration.statistics()

    assert stats["name"] == "MetricQTCIntegration"
    assert stats["configured"] is False
    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0


def test_status_empty():

    integration = MetricQTCIntegration()

    status = integration.status()

    assert status["configured"] is False
    assert status["active"] is False
    assert status["valid"] is True


def test_status_valid():

    integration = MetricQTCIntegration(
        qtc=EvaluateQTC(),
    )

    status = integration.status()

    assert status["configured"] is True
    assert status["active"] is True
    assert status["valid"] is True


def test_reset():

    integration = MetricQTCIntegration()

    integration.execute(
        {"value": 1},
    )

    assert integration.statistics()["executions"] == 1

    assert integration.reset() is integration

    assert integration.statistics()["executions"] == 0
    assert integration.statistics()["success"] == 0
    assert integration.statistics()["failures"] == 0

    assert integration.last_result is None
    assert integration.last_error is None


# ==============================================================
# Protocols
# ==============================================================


def test_len():

    integration = MetricQTCIntegration()

    assert len(integration) == 0

    integration.execute({"value": 1})

    assert len(integration) == 1


def test_repr():

    integration = MetricQTCIntegration()

    value = repr(integration)

    assert "MetricQTCIntegration" in value
    assert "configured=False" in value


def test_str():

    integration = MetricQTCIntegration()

    assert str(integration) == "MetricQTCIntegration"