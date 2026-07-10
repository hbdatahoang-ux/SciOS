# tests/test_monitor.py

import pytest
import time
from scios.cognitive_core.tool_use.monitor import Monitor


def test_monitor_initialization_and_schema():
    m = Monitor()
    assert m.entries == []
    data = m.to_dict()
    required_keys = {"entries"}
    assert required_keys.issubset(data.keys())
    assert isinstance(data["entries"], list)
    assert data["entries"] == []


def test_monitor_start_and_end_success():
    m = Monitor()
    m.start("task1")
    time.sleep(0.1)
    m.end("task1", status="success")

    assert len(m.entries) == 1
    entry = m.entries[0]
    assert entry["task"] == "task1"
    assert entry["status"] == "success"
    assert entry["duration"] >= 0.1


def test_monitor_start_and_end_error():
    m = Monitor()
    m.start("task2")
    m.end("task2", status="error", message="Something failed")

    entry = m.entries[0]
    assert entry["status"] == "error"
    assert "Something failed" in entry["message"]


def test_monitor_multiple_tasks_fifo_order():
    m = Monitor()
    m.start("A")
    m.end("A", status="success")
    m.start("B")
    m.end("B", status="success")

    assert m.entries[0]["task"] == "A"
    assert m.entries[1]["task"] == "B"


def test_monitor_clear_entries():
    m = Monitor()
    m.start("X")
    m.end("X", status="success")
    assert len(m.entries) == 1

    m.clear()
    assert m.entries == []
    assert m.to_dict()["entries"] == []


def test_monitor_repr_shows_count():
    m = Monitor()
    m.start("Y")
    m.end("Y", status="success")
    repr_str = repr(m)
    assert "entries=1" in repr_str
