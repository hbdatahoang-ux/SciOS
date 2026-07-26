"""
Tests for runtime metadata injection.

Responsibilities
----------------
- System metadata
- Runtime metadata
- User metadata
- Merge precedence
- Metadata immutability
"""

from __future__ import annotations

import platform
import socket

import pytest

from .builders import PluginBuilder


# ============================================================
# System Metadata
# ============================================================


def test_system_metadata(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    trace = plugin.manager.current_trace

    attrs = trace.attributes

    assert "system.hostname" in attrs
    assert "system.platform" in attrs
    assert "system.python" in attrs

    assert attrs["system.hostname"] == socket.gethostname()

    assert attrs["system.platform"] == platform.system()

    assert platform.python_version() in attrs["system.python"]


def test_system_metadata_exists_only_once(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    trace = plugin.manager.current_trace

    attrs = trace.attributes

    assert list(attrs.keys()).count(
        "system.hostname"
    ) == 1

    assert list(attrs.keys()).count(
        "system.platform"
    ) == 1


# ============================================================
# Runtime Metadata
# ============================================================


def test_runtime_name_metadata(plugin):

    plugin.before_runtime(
        runtime_name="InferenceRuntime",
    )

    trace = plugin.manager.current_trace

    assert (
        trace.attributes["runtime.name"]
        == "InferenceRuntime"
    )


def test_runtime_version_metadata(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        runtime_version="0.9.1",
    )

    trace = plugin.manager.current_trace

    assert (
        trace.attributes["runtime.version"]
        == "0.9.1"
    )


def test_runtime_id_metadata(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        runtime_id="node-001",
    )

    trace = plugin.manager.current_trace

    assert (
        trace.attributes["runtime.id"]
        == "node-001"
    )


# ============================================================
# User Metadata
# ============================================================


def test_custom_metadata(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata={
            "dataset": "ImageNet",
            "batch": 64,
            "gpu": "A100",
        },
    )

    trace = plugin.manager.current_trace

    assert trace.attributes["dataset"] == "ImageNet"

    assert trace.attributes["batch"] == 64

    assert trace.attributes["gpu"] == "A100"


def test_empty_metadata(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata={},
    )

    trace = plugin.manager.current_trace

    assert trace is not None


# ============================================================
# Merge Order
# ============================================================


def test_user_metadata_does_not_remove_system_metadata(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata={
            "project": "SciOS",
        },
    )

    trace = plugin.manager.current_trace

    attrs = trace.attributes

    assert "system.hostname" in attrs

    assert attrs["project"] == "SciOS"


def test_runtime_metadata_has_priority_over_user_override(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata={
            "runtime.name": "WrongRuntime",
        },
    )

    trace = plugin.manager.current_trace

    #
    # runtime.name should always reflect
    # actual runtime
    #
    assert (
        trace.attributes["runtime.name"]
        == "Runtime"
    )


# ============================================================
# Immutability
# ============================================================


def test_original_metadata_not_modified(plugin):

    metadata = {
        "dataset": "COCO",
    }

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata=metadata,
    )

    metadata["dataset"] = "Changed"

    trace = plugin.manager.current_trace

    assert (
        trace.attributes["dataset"]
        == "COCO"
    )


def test_trace_metadata_is_independent_between_runs(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata={
            "dataset": "A",
        },
    )

    trace1 = plugin.manager.current_trace

    plugin.after_runtime()

    plugin.before_runtime(
        runtime_name="Runtime",
        metadata={
            "dataset": "B",
        },
    )

    trace2 = plugin.manager.current_trace

    assert trace1.attributes["dataset"] == "A"

    assert trace2.attributes["dataset"] == "B"