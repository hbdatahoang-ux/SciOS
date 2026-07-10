# tests/test_metrics.py

import pytest
import time
from scios.cognitive_core.tool_use.metrics import Metrics


def test_metrics_initialization_and_schema():
    m = Metrics()
    assert m.count_success == 0
    assert m.count_error == 0
    assert m.total_time == 0.0

    data = m.to_dict()
    required_keys = {"success", "error", "avg_time"}
    assert required_keys.issubset(data.keys())
    assert data["success"] == 0
    assert data["error"] == 0
    assert data["avg_time"] == 0.0


def test_metrics_record_success_and_error():
    m = Metrics()
    m.record_success(duration=0.5)
    m.record_error(duration=1.0)

    assert m.count_success == 1
    assert m.count_error == 1
    assert m.total_time >= 1.5

    data = m.to_dict()
    assert data["success"] == 1
    assert data["error"] == 1
    assert data["avg_time"] > 0.0


def test_metrics_average_time_calculation():
    m = Metrics()
    m.record_success(duration=1.0)
    m.record_success(duration=2.0)
    m.record_error(duration=3.0)

    avg = m.average_time()
    # Tổng thời gian = 6.0, số lần = 3 → avg = 2.0
    assert pytest.approx(avg, 0.01) == 2.0


def test_metrics_reset():
    m = Metrics()
    m.record_success(duration=0.5)
    m.record_error(duration=1.0)
    assert m.count_success == 1
    assert m.count_error == 1

    m.reset()
    assert m.count_success == 0
    assert m.count_error == 0
    assert m.total_time == 0.0


def test_metrics_repr_shows_counts():
    m = Metrics()
    m.record_success(duration=0.5)
    m.record_error(duration=1.0)

    repr_str = repr(m)
    assert "success=1" in repr_str
    assert "error=1" in repr_str
