from __future__ import annotations

import inspect

from scios.runtime.observability.metrics.core.metrics.registry.statistics import (
    MetricStatistics,
    __all__,
)


# ==============================================================================
# Constructor
# ==============================================================================


def test_default_constructor():

    stats = MetricStatistics()

    assert stats.name == ""
    assert stats.count == 0
    assert stats.sum == 0.0
    assert stats.minimum is None
    assert stats.maximum is None
    assert stats.state == {}


def test_custom_constructor():

    stats = MetricStatistics(
        name="runtime",
        count=10,
        sum=25.5,
        minimum=1.0,
        maximum=5.0,
    )

    assert stats.name == "runtime"
    assert stats.count == 10
    assert stats.sum == 25.5
    assert stats.minimum == 1.0
    assert stats.maximum == 5.0


def test_slots():

    assert hasattr(
        MetricStatistics,
        "__slots__",
    )


def test_annotations():

    annotations = MetricStatistics.__annotations__

    assert "name" in annotations
    assert "count" in annotations
    assert "sum" in annotations
    assert "minimum" in annotations
    assert "maximum" in annotations
    assert "state" in annotations


def test_signature():

    signature = inspect.signature(
        MetricStatistics,
    )

    assert "name" in signature.parameters
    assert "count" in signature.parameters


# ==============================================================================
# Properties
# ==============================================================================


def test_name_property():

    stats = MetricStatistics(
        name="runtime",
    )

    assert stats.name == "runtime"


def test_count_property():

    stats = MetricStatistics(
        count=5,
    )

    assert stats.count == 5


def test_sum_property():

    stats = MetricStatistics(
        sum=15.0,
    )

    assert stats.sum == 15.0


def test_minimum_property():

    stats = MetricStatistics(
        minimum=2.0,
    )

    assert stats.minimum == 2.0


def test_maximum_property():

    stats = MetricStatistics(
        maximum=8.0,
    )

    assert stats.maximum == 8.0


def test_state_property():

    stats = MetricStatistics()

    assert isinstance(
        stats.state,
        dict,
    )

# ==============================================================================
# Utilities
# ==============================================================================

def test_clone():

    statistics = MetricStatistics(
        name="runtime",
    )

    cloned = statistics.clone()

    assert cloned is not statistics

    assert cloned == statistics


def test_copy():

    statistics = MetricStatistics(
        name="runtime",
    )

    copied = statistics.copy()

    assert copied is not statistics

    assert copied == statistics


def test_merge():

    a = MetricStatistics()

    b = MetricStatistics()

    b.count = 10

    b.sum = 50.0

    a.merge(b)

    assert a.count == 10

    assert a.sum == 50.0


def test_update():

    a = MetricStatistics()

    b = MetricStatistics()

    b.count = 5

    b.minimum = 1.0

    a.update(b)

    assert a.count == 5

    assert a.minimum == 1.0


def test_reset():

    statistics = MetricStatistics()

    statistics.count = 10

    statistics.sum = 100.0

    statistics.maximum = 20.0

    statistics.reset()

    assert statistics.count == 0

    assert statistics.sum == 0.0

    assert statistics.maximum == 0.0


# ==============================================================================
# Protocols
# ==============================================================================

def test_hash():

    statistics = MetricStatistics()

    assert isinstance(
        hash(statistics),
        int,
    )


def test_eq():

    a = MetricStatistics()

    b = MetricStatistics()

    assert a == b


def test_repr():

    statistics = MetricStatistics()

    text = repr(statistics)

    assert "MetricStatistics" in text


def test_str():

    statistics = MetricStatistics()

    text = str(statistics)

    assert isinstance(
        text,
        str,
    )


def test_bool():

    statistics = MetricStatistics()

    assert not statistics

    statistics.count = 1

    assert statistics


# ==============================================================================
# Diagnostics
# ==============================================================================

def test_summary():

    statistics = MetricStatistics()

    summary = statistics.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert "count" in summary


def test_diagnostics():

    statistics = MetricStatistics()

    diagnostics = statistics.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )

    assert "valid" in diagnostics


def test_statistics_report():

    statistics = MetricStatistics()

    report = statistics.statistics_report()

    assert isinstance(
        report,
        dict,
    )

    assert "summary" in report


def test_overall_status():

    statistics = MetricStatistics()

    assert (
        statistics.overall_status()
        == "healthy"
    )


# ==============================================================================
# Public API
# ==============================================================================

def test_public_api():

    assert "MetricStatistics" in __all__    