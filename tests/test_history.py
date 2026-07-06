# tests/test_history.py
import pytest
from scios.cognitive_core.reflection.history import ReflectionHistory

def test_store_and_latest():
    history = ReflectionHistory()
    report1 = {"evaluation": {"success": True}}
    report2 = {"evaluation": {"success": False}}

    history.store(report1)
    history.store(report2)

    # Latest phải là report2
    latest = history.latest()
    assert latest == report2
    assert history.count() == 2

def test_all_reports():
    history = ReflectionHistory()
    reports = [
        {"evaluation": {"success": True}},
        {"evaluation": {"success": False}},
    ]
    for r in reports:
        history.store(r)

    all_reports = history.all()
    assert all_reports == reports
    assert len(all_reports) == 2

def test_clear_history():
    history = ReflectionHistory()
    history.store({"evaluation": {"success": True}})
    assert history.count() == 1

    history.clear()
    assert history.count() == 0
    assert history.latest() is None
    assert history.all() == []

def test_repr_shows_count():
    history = ReflectionHistory()
    history.store({"evaluation": {"success": True}})
    repr_str = repr(history)
    assert "entries=1" in repr_str
