"""
SciOS ServiceRegistry Tests
===========================

Validate:
- Register service
- Unregister service
- Lookup service
- Names and count
"""

import pytest
from scios.kernel.registry import ServiceRegistry


class DummyService:
    def __init__(self, name="dummy"):
        self.name = name
        self.state = "initialized"


def test_register_and_get_service():
    registry = ServiceRegistry()
    service = DummyService()
    registry.register("planner", service)

    retrieved = registry.get("planner")
    assert isinstance(retrieved, DummyService)
    assert retrieved.name == "dummy"


def test_unregister_service():
    registry = ServiceRegistry()
    service = DummyService()
    registry.register("executor", service)

    assert "executor" in registry
    registry.unregister("executor")
    assert "executor" not in registry


def test_names_and_count():
    registry = ServiceRegistry()
    registry.register("a", DummyService("A"))
    registry.register("b", DummyService("B"))

    names = registry.names()
    assert "a" in names and "b" in names
    assert registry.count() == 2
    assert len(registry) == 2


def test_get_nonexistent_service_returns_none():
    registry = ServiceRegistry()
    assert registry.get("nonexistent") is None
