# tests/test_history.py

import pytest
from scios.cognitive_core.reflection.history import ReflectionHistory


def test_history_initialization_and_empty_state():
    history = ReflectionHistory()
    assert history.count() == 0
    assert history.latest() is None
    assert history.all() == []
    assert "entries=0" in repr(history)


def test_store_and_latest_report():
    history = ReflectionHistory()
    report1 = {"evaluation": {"success": True}}
    report2 = {"evaluation": {"success": False}}

    history.store(report1)
    history.store(report2)

    latest = history.latest()
    assert latest == report2
    assert history.count() == 2
    assert "entries=2" in repr(history)


def test_all_reports_preserve_order():
    history = ReflectionHistory()
    reports = [
        {"evaluation": {"success": True}},
        {"evaluation": {"success": False}},
        {"evaluation": {"success": True, "details": "third"}},
    ]
    for r in reports:
        history.store(r)

    all_reports = history.all()
    assert all_reports == reports
    assert len(all_reports) == 3
    # Đảm bảo thứ tự được giữ nguyên
    assert all_reports[0]["evaluation"]["success"] is True
    assert all_reports[1]["evaluation"]["success"] is False
    assert all_reports[2]["evaluation"]["details"] == "third"


def test_clear_history_resets_state():
    history = ReflectionHistory()
    history.store({"evaluation": {"success": True}})
    assert history.count() == 1

    history.clear()
    assert history.count() == 0
    assert history.latest() is None
    assert history.all() == []
    assert "entries=0" in repr(history)


def test_repr_shows_correct_count():
    history = ReflectionHistory()
    history.store({"evaluation": {"success": True}})
    history.store({"evaluation": {"success": False}})
    repr_str = repr(history)
    assert "entries=2" in repr_str
