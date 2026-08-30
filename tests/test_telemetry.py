"""
SciOS Runtime Telemetry Tests
=============================

Tests for TelemetryPlugin.

Goals
-----
- Verify automatic metric collection.
- Verify runtime lifecycle integration.
- Verify latency measurement.
- Verify success/failure accounting.
- Verify plugin lifecycle.
- Verify report/snapshot schema.
"""

from __future__ import annotations

import time

from scios.runtime.engine import ExecutionEngine
from scios.runtime.result import ExecutionResult
from scios.runtime.telemetry import TelemetryPlugin


# ==========================================================
# Helpers
# ==========================================================


class SuccessWorker:
    """
    Worker that returns a successful ExecutionResult.
    """

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def status(self) -> dict:
        return {}

    def execute(self, context):
        time.sleep(0.01)

        return ExecutionResult.ok(
            "ok",
        )


class FailureWorker:
    """
    Worker that returns a failed ExecutionResult.
    """

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def status(self) -> dict:
        return {}

    def execute(self, context):
        time.sleep(0.01)

        return ExecutionResult.fail(
            RuntimeError("boom"),
        )


# ==========================================================
# Construction
# ==========================================================


def test_construct() -> None:
    """
    TelemetryPlugin should be constructible and start empty.
    """

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    assert plugin is not None
    assert plugin.metrics.total_tasks == 0


# ==========================================================
# Install
# ==========================================================


def test_install() -> None:
    """
    Installing the plugin should activate telemetry collection.
    """

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    plugin.install()

    assert plugin.installed


# ==========================================================
# Successful Execution
# ==========================================================


def test_success_metrics() -> None:
    """
    Successful executions should update success metrics.
    """

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    context = engine.run("task")

    report = plugin.report()

    # Runtime execution
    assert context.status == "completed"
    assert context.has_result
    assert context.success

    # Result contract
    result = context.get_execution_result()

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.value == "ok"

    # Telemetry contract
    assert report["total_tasks"] == 1
    assert report["completed_tasks"] == 1
    assert report["failed_tasks"] == 0
    assert report["running_tasks"] == 0
    assert report["success_rate"] == 1.0


# ==========================================================
# Failed Execution
# ==========================================================


def test_failure_metrics() -> None:
    """
    Failed executions should update failure metrics.
    """

    engine = ExecutionEngine(
        worker=FailureWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    context = engine.run("task")

    report = plugin.report()

    # Runtime execution
    assert context.status == "failed"
    assert context.has_result
    assert context.failed

    # Result contract
    result = context.get_execution_result()

    assert isinstance(result, ExecutionResult)
    assert result.success is False
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "boom"

    # Telemetry contract
    assert report["total_tasks"] == 1
    assert report["completed_tasks"] == 0
    assert report["failed_tasks"] == 1
    assert report["running_tasks"] == 0
    assert report["success_rate"] == 0.0


# ==========================================================
# Latency
# ==========================================================


def test_latency() -> None:
    """
    Successful execution should produce a positive latency.
    """

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    engine.run("task")

    report = plugin.report()

    assert report["average_latency"] > 0
    assert report["max_latency"] >= report["min_latency"]
    assert report["min_latency"] > 0


# ==========================================================
# Multiple Tasks
# ==========================================================


def test_multiple_tasks() -> None:
    """
    Telemetry should aggregate multiple successful executions.
    """

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    for index in range(5):
        engine.run(
            f"task-{index}",
        )

    report = plugin.report()

    assert report["total_tasks"] == 5
    assert report["completed_tasks"] == 5
    assert report["failed_tasks"] == 0
    assert report["running_tasks"] == 0
    assert report["success_rate"] == 1.0

    assert report["average_latency"] > 0
    assert report["max_latency"] >= report["min_latency"]


# ==========================================================
# Plugin Lifecycle
# ==========================================================


def test_uninstall() -> None:
    """
    Uninstalling the plugin should remove all registered hooks.
    """

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    plugin.install()

    assert plugin.installed

    plugin.uninstall()

    assert not plugin.installed
    assert len(plugin.handles) == 0


# ==========================================================
# Snapshot / Report Schema
# ==========================================================


def test_snapshot() -> None:
    """
    Telemetry report should expose the stable metric schema.
    """

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    report = plugin.report()

    expected = {
        "total_tasks",
        "running_tasks",
        "completed_tasks",
        "failed_tasks",
        "success_rate",
        "average_latency",
        "max_latency",
        "min_latency",
    }

    assert isinstance(report, dict)
    assert expected <= set(report)