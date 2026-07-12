"""
SciOS Runtime Telemetry Tests
=============================

Tests for the Runtime TelemetryPlugin.

Coverage
--------
- Plugin construction
- Installation
- Successful execution metrics
- Failed execution metrics
- Latency collection
- Multiple executions
- Plugin uninstall
- Metrics snapshot

Runtime API
-----------
ExecutionResult.ok(...)
ExecutionResult.fail(...)
"""

from __future__ import annotations

import time

from scios.runtime.engine import ExecutionEngine
from scios.runtime.result import ExecutionResult
from scios.runtime.telemetry import TelemetryPlugin


# ==========================================================
# Test Workers
# ==========================================================


class SuccessWorker:
    """
    Worker returning a successful ExecutionResult.
    """

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def status(self):
        return {}

    def execute(self, context):

        time.sleep(0.01)

        return ExecutionResult.ok(
            value="ok"
        )


class FailureWorker:
    """
    Worker returning a failed ExecutionResult.
    """

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def status(self):
        return {}

    def execute(self, context):

        time.sleep(0.01)

        return ExecutionResult.fail(
            RuntimeError("boom")
        )


# ==========================================================
# Construction
# ==========================================================


def test_construct():

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    assert plugin.metrics.total_tasks == 0
    assert plugin.metrics.running_tasks == 0
    assert plugin.metrics.completed_tasks == 0
    assert plugin.metrics.failed_tasks == 0
    assert plugin.metrics.latencies == []


# ==========================================================
# Installation
# ==========================================================


def test_install():

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    plugin.install()

    assert plugin.installed

    assert len(plugin.handles) == 4


# ==========================================================
# Successful execution
# ==========================================================


def test_success_metrics():

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    context = engine.run("task")

    report = plugin.report()

    assert context.completed
    assert context.result.success

    assert report["total_tasks"] == 1
    assert report["running_tasks"] == 0
    assert report["completed_tasks"] == 1
    assert report["failed_tasks"] == 0

    assert report["success_rate"] == 1.0

    assert report["average_latency"] > 0.0
    assert report["max_latency"] >= report["min_latency"]


# ==========================================================
# Failed execution
# ==========================================================


def test_failure_metrics():

    engine = ExecutionEngine(
        worker=FailureWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    context = engine.run("task")

    report = plugin.report()

    assert context.failed
    assert context.result.failed

    assert report["total_tasks"] == 1
    assert report["running_tasks"] == 0
    assert report["completed_tasks"] == 0
    assert report["failed_tasks"] == 1

    assert report["success_rate"] == 0.0


# ==========================================================
# Latency
# ==========================================================


def test_latency():

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    engine.run("task")

    report = plugin.report()

    assert report["average_latency"] > 0.0
    assert report["max_latency"] > 0.0
    assert report["min_latency"] > 0.0

    assert report["max_latency"] >= report["average_latency"]
    assert report["average_latency"] >= report["min_latency"]


# ==========================================================
# Multiple executions
# ==========================================================


def test_multiple_tasks():

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    for _ in range(5):

        context = engine.run("task")

        assert context.completed

    report = plugin.report()

    assert report["total_tasks"] == 5
    assert report["completed_tasks"] == 5
    assert report["failed_tasks"] == 0
    assert report["running_tasks"] == 0

    assert report["success_rate"] == 1.0

    assert len(plugin.metrics.latencies) == 5


# ==========================================================
# Plugin lifecycle
# ==========================================================


def test_uninstall():

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    plugin.install()

    assert plugin.installed
    assert len(plugin.handles) == 4

    plugin.uninstall()

    assert not plugin.installed
    assert len(plugin.handles) == 0


# ==========================================================
# Snapshot
# ==========================================================


def test_snapshot():

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

    assert expected <= report.keys()


# ==========================================================
# Metrics consistency
# ==========================================================


def test_metrics_consistency():

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    for _ in range(3):
        engine.run("task")

    report = plugin.report()

    assert (
        report["completed_tasks"]
        +
        report["failed_tasks"]
        ==
        report["total_tasks"]
    )

    assert report["running_tasks"] == 0

