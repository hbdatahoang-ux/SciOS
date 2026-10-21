"""
Tests for MetricExporterIntegration.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from ..exporter_integration import (
    MetricExporterIntegration,
)


# ==============================================================
# Helpers
# ==============================================================


class Exporter:

    def __init__(self, name="Exporter"):
        self.name = name
        self.calls = 0
        self.closed = False
        self.flushed = False

    def export(self, metric, **kwargs):
        self.calls += 1

        return {
            **metric,
            self.name: True,
        }

    def close(self):
        self.closed = True

    def flush(self):
        self.flushed = True


class ProcessExporter:

    def process(self, metric, **kwargs):
        return {
            **metric,
            "processed": True,
        }


class ExecuteExporter:

    def execute(self, metric, **kwargs):
        return {
            **metric,
            "executed": True,
        }


@pytest.fixture
def exporter():
    return Exporter()


@pytest.fixture
def second_exporter():
    return Exporter("Second")


@pytest.fixture
def integration(
    exporter,
    second_exporter,
):
    return MetricExporterIntegration(
        exporters=[
            exporter,
            second_exporter,
        ]
    )


# ==============================================================
# Constructor
# ==============================================================


def test_default_constructor():

    integration = MetricExporterIntegration()

    assert integration.name == "MetricExporterIntegration"
    assert integration.description == ""
    assert integration.exporters_count == 0
    assert integration.last_result is None
    assert integration.last_error is None


def test_constructor_exporters(
    integration,
    exporter,
    second_exporter,
):

    assert integration.exporters() == [
        exporter,
        second_exporter,
    ]

    assert integration.exporters_count == 2


# ==============================================================
# Exporter Management
# ==============================================================


def test_add_exporter():

    integration = MetricExporterIntegration()
    exporter = Exporter()

    assert integration.add_exporter(exporter) is integration
    assert exporter in integration


def test_add_none():

    integration = MetricExporterIntegration()

    with pytest.raises(
        ValueError,
        match="must not be None",
    ):
        integration.add_exporter(None)


def test_add_invalid():

    integration = MetricExporterIntegration()

    with pytest.raises(
        TypeError,
        match="supported execution",
    ):
        integration.add_exporter(object())


def test_remove_exporter(
    integration,
    exporter,
):

    assert integration.remove_exporter(exporter) is integration
    assert exporter not in integration
    assert integration.exporters_count == 1


def test_remove_missing_exporter(
    integration,
):

    exporter = Exporter()

    assert integration.remove_exporter(exporter) is integration
    assert integration.exporters_count == 2


def test_clear_exporters(
    integration,
):

    assert integration.clear_exporters() is integration
    assert integration.exporters() == []
    assert integration.exporters_count == 0


def test_get_exporter(
    integration,
    exporter,
    second_exporter,
):

    assert integration.get_exporter(0) is exporter
    assert integration.get_exporter(1) is second_exporter


def test_get_exporter_invalid_index(
    integration,
):

    with pytest.raises(IndexError):
        integration.get_exporter(99)


# ==============================================================
# Execution
# ==============================================================


def test_execute(
    integration,
):

    result = integration.execute(
        {"value": 1}
    )

    assert result == {
        "value": 1,
        "Exporter": True,
        "Second": True,
    }

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1
    assert stats["failures"] == 0


def test_export_alias(
    integration,
):

    result = integration.export(
        {"value": 1}
    )

    assert result["Second"] is True


def test_process_alias(
    integration,
):

    result = integration.process(
        {"value": 1}
    )

    assert result["Second"] is True


def test_run_alias(
    integration,
):

    result = integration.run(
        {"value": 1}
    )

    assert result["Second"] is True


def test_call(
    integration,
):

    result = integration(
        {"value": 1}
    )

    assert result["Second"] is True


def test_execution_order(
    integration,
    exporter,
    second_exporter,
):

    integration.execute(
        {"value": 1}
    )

    assert exporter.calls == 1
    assert second_exporter.calls == 1


def test_empty_integration():

    integration = MetricExporterIntegration()

    metric = {
        "value": 42,
    }

    assert integration.execute(metric) == metric

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 1


# ==============================================================
# Exporter API Compatibility
# ==============================================================


def test_process_exporter():

    integration = MetricExporterIntegration(
        exporters=[
            ProcessExporter()
        ]
    )

    result = integration.export(
        {"value": 1}
    )

    assert result["processed"] is True


def test_execute_exporter():

    integration = MetricExporterIntegration(
        exporters=[
            ExecuteExporter()
        ]
    )

    result = integration.export(
        {"value": 1}
    )

    assert result["executed"] is True


def test_callable_exporter():

    integration = MetricExporterIntegration(
        exporters=[
            lambda metric, **kwargs: {
                **metric,
                "callable": True,
            }
        ]
    )

    result = integration.export(
        {"value": 1}
    )

    assert result["callable"] is True


# ==============================================================
# Batch Execution
# ==============================================================


def test_execute_many(
    integration,
):

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


def test_export_many(
    integration,
):

    results = integration.export_many(
        [
            {"value": 1},
            {"value": 2},
        ]
    )

    assert len(results) == 2


def test_process_many(
    integration,
):

    results = integration.process_many(
        [
            {"value": 1},
            {"value": 2},
        ]
    )

    assert len(results) == 2


# ==============================================================
# Error Handling
# ==============================================================


def test_export_failure():

    error = RuntimeError("boom")

    def failing(metric):
        raise error

    integration = MetricExporterIntegration(
        exporters=[failing]
    )

    with pytest.raises(
        RuntimeError,
        match="boom",
    ):
        integration.export({})

    stats = integration.statistics()

    assert stats["executions"] == 1
    assert stats["success"] == 0
    assert stats["failures"] == 1

    assert integration.last_error is error
    assert integration.last_result is None


# ==============================================================
# Validation
# ==============================================================


def test_validate_empty():

    integration = MetricExporterIntegration()

    assert integration.validate_chain() is True


def test_validate_valid(
    integration,
):

    assert integration.validate_chain() is True


def test_validate_invalid():

    integration = MetricExporterIntegration()

    integration._exporters.append(object())

    assert integration.validate_chain() is False


# ==============================================================
# Lifecycle
# ==============================================================


def test_close(
    integration,
    exporter,
    second_exporter,
):

    assert integration.close() is integration

    assert exporter.closed is True
    assert second_exporter.closed is True


def test_flush(
    integration,
    exporter,
    second_exporter,
):

    assert integration.flush() is integration

    assert exporter.flushed is True
    assert second_exporter.flushed is True


# ==============================================================
# Diagnostics
# ==============================================================


def test_statistics_initial(
    integration,
):

    stats = integration.statistics()

    assert stats["name"] == "MetricExporterIntegration"
    assert stats["exporters"] == 2
    assert stats["executions"] == 0
    assert stats["success"] == 0
    assert stats["failures"] == 0


def test_status(
    integration,
):

    status = integration.status()

    assert status["exporters"] == 2
    assert status["active"] is True
    assert status["valid"] is True


def test_reset(
    integration,
):

    integration.export(
        {"value": 1}
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


def test_len(
    integration,
):

    assert len(integration) == 2


def test_iter(
    integration,
    exporter,
    second_exporter,
):

    assert list(integration) == [
        exporter,
        second_exporter,
    ]


def test_contains(
    integration,
    exporter,
):

    assert exporter in integration


def test_repr(
    integration,
):

    value = repr(integration)

    assert "MetricExporterIntegration" in value
    assert "exporters=2" in value


def test_str(
    integration,
):

    assert str(integration) == "MetricExporterIntegration"