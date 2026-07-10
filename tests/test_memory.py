"""
SciOS Memory Tests
==================

Foundation tests for the SciOS memory abstraction.

These tests validate the stable memory contract independently of the
underlying memory implementation.
"""

from __future__ import annotations

import pytest

from scios.agents.memory.working import WorkingMemory


# ==========================================================
# Construction
# ==========================================================

def test_memory_construction() -> None:
    """
    Memory should be constructible.
    """

    memory = WorkingMemory()

    assert memory is not None


# ==========================================================
# Initially Empty
# ==========================================================

def test_memory_initially_empty() -> None:
    """
    Newly created memory should be empty.
    """

    memory = WorkingMemory()

    assert len(memory) == 0
    assert memory.empty()


# ==========================================================
# Store
# ==========================================================

def test_store() -> None:
    """
    Objects should be stored successfully.
    """

    memory = WorkingMemory()

    memory.store(
        key="a",
        value=123,
    )

    assert len(memory) == 1


# ==========================================================
# Retrieve
# ==========================================================

def test_retrieve() -> None:
    """
    Stored objects should be retrievable.
    """

    memory = WorkingMemory()

    memory.store(
        key="answer",
        value=42,
    )

    assert memory.retrieve("answer") == 42


# ==========================================================
# Missing Key
# ==========================================================

def test_missing_key() -> None:
    """
    Retrieving a missing key should fail.
    """

    memory = WorkingMemory()

    with pytest.raises(KeyError):
        memory.retrieve("missing")


# ==========================================================
# Exists
# ==========================================================

def test_exists() -> None:
    """
    Membership queries should work.
    """

    memory = WorkingMemory()

    memory.store("x", 1)

    assert memory.exists("x")
    assert not memory.exists("y")


# ==========================================================
# Remove
# ==========================================================

def test_remove() -> None:
    """
    Removing an entry should delete it.
    """

    memory = WorkingMemory()

    memory.store("k", "v")

    memory.remove("k")

    assert not memory.exists("k")


# ==========================================================
# Clear
# ==========================================================

def test_clear() -> None:
    """
    Clearing memory should remove everything.
    """

    memory = WorkingMemory()

    for i in range(10):
        memory.store(str(i), i)

    memory.clear()

    assert len(memory) == 0
    assert memory.empty()


# ==========================================================
# Overwrite
# ==========================================================

def test_overwrite() -> None:
    """
    Existing values should be replaceable.
    """

    memory = WorkingMemory()

    memory.store("x", 1)
    memory.store("x", 2)

    assert memory.retrieve("x") == 2


# ==========================================================
# Multiple Entries
# ==========================================================

def test_multiple_entries() -> None:
    """
    Memory should support many entries.
    """

    memory = WorkingMemory()

    for i in range(100):

        memory.store(
            str(i),
            i,
        )

    assert len(memory) == 100

    for i in range(100):

        assert memory.retrieve(str(i)) == i


# ==========================================================
# Keys
# ==========================================================

def test_keys() -> None:
    """
    Memory should expose keys().
    """

    memory = WorkingMemory()

    memory.store("a", 1)
    memory.store("b", 2)

    keys = memory.keys()

    assert "a" in keys
    assert "b" in keys


# ==========================================================
# Values
# ==========================================================

def test_values() -> None:
    """
    Memory should expose values().
    """

    memory = WorkingMemory()

    memory.store("a", 10)
    memory.store("b", 20)

    values = memory.values()

    assert 10 in values
    assert 20 in values


# ==========================================================
# Items
# ==========================================================

def test_items() -> None:
    """
    Memory should expose items().
    """

    memory = WorkingMemory()

    memory.store("a", 1)

    items = dict(memory.items())

    assert items["a"] == 1


# ==========================================================
# Status
# ==========================================================

def test_status_schema() -> None:
    """
    Memory should expose a stable status schema.
    """

    memory = WorkingMemory()

    status = memory.status()

    required = {
        "entries",
        "capacity",
    }

    assert required.issubset(status.keys())


# ==========================================================
# Capacity
# ==========================================================

def test_capacity_limit() -> None:
    """
    Memory should enforce capacity.
    """

    memory = WorkingMemory(capacity=2)

    memory.store("a", 1)
    memory.store("b", 2)

    with pytest.raises(Exception):
        memory.store("c", 3)


# ==========================================================
# Iteration
# ==========================================================

def test_iteration() -> None:
    """
    Memory should be iterable.
    """

    memory = WorkingMemory()

    memory.store("a", 1)
    memory.store("b", 2)

    keys = {k for k, _ in memory}

    assert keys == {"a", "b"}
