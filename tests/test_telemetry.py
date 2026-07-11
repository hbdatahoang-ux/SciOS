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
"""

from __future__ import annotations

import time

from scios.runtime.engine import ExecutionEngine
from scios.runtime.telemetry import TelemetryPlugin
from scios.runtime.result import ExecutionResult


# ==========================================================
# Helpers
# ==========================================================

class SuccessWorker:

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
        return ExecutionResult.success(result="ok")


class FailureWorker:

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
        return ExecutionResult.fail(RuntimeError("boom"))


# ==========================================================
# Construction
# ==========================================================

def test_construct():

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    assert plugin.metrics.total_tasks == 0


# ==========================================================
# Install
# ==========================================================

def test_install():

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    plugin.install()

    assert plugin.installed


# ==========================================================
# Successful execution
# ==========================================================

def test_success_metrics():

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    engine.run("task")

    report = plugin.report()

    assert report["total_tasks"] == 1

    assert report["completed_tasks"] == 1

    assert report["failed_tasks"] == 0

    assert report["running_tasks"] == 0

    assert report["success_rate"] == 1.0


# ==========================================================
# Failed execution
# ==========================================================

def test_failure_metrics():

    engine = ExecutionEngine(
        worker=FailureWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    engine.run("task")

    report = plugin.report()

    assert report["total_tasks"] == 1

    assert report["completed_tasks"] == 0

    assert report["failed_tasks"] == 1

    assert report["running_tasks"] == 0

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

    assert report["average_latency"] > 0

    assert report["max_latency"] >= report["min_latency"]


# ==========================================================
# Multiple tasks
# ==========================================================

def test_multiple_tasks():

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    plugin = TelemetryPlugin(engine)

    plugin.install()

    for _ in range(5):
        engine.run("task")

    report = plugin.report()

    assert report["total_tasks"] == 5

    assert report["completed_tasks"] == 5

    assert report["failed_tasks"] == 0


# ==========================================================
# Plugin lifecycle
# ==========================================================

def test_uninstall():

    engine = ExecutionEngine()

    plugin = TelemetryPlugin(engine)

    plugin.install()

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

    assert expected <= set(report)