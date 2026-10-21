"""
SciOS Runtime Agent Memory Tests
================================

Contract tests for the Memory abstraction.

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.agent.memory import Memory


# ==========================================================
# Construction
# ==========================================================


def test_memory_creation() -> None:

    memory = Memory()

    assert len(memory) == 0
    assert memory.size == 0
    assert memory.writes == 0
    assert memory.reads == 0


# ==========================================================
# Store
# ==========================================================


def test_memory_store() -> None:

    memory = Memory()

    memory.store(
        "greeting",
        "hello",
    )

    assert memory.get("greeting") == "hello"
    assert memory.writes == 1


def test_memory_store_overwrite() -> None:

    memory = Memory()

    memory.store(
        "key",
        "first",
    )

    memory.store(
        "key",
        "second",
    )

    assert memory.get("key") == "second"
    assert memory.writes == 2
    assert len(memory) == 1


def test_memory_store_requires_string_key() -> None:

    memory = Memory()

    with pytest.raises(
        TypeError,
        match="key must be a string",
    ):
        memory.store(
            123,
            "value",
        )


# ==========================================================
# Add
# ==========================================================


def test_memory_add() -> None:

    memory = Memory()

    key = memory.add(
        "hello"
    )

    assert key == "memory-0"
    assert memory.get(key) == "hello"


def test_memory_add_generates_unique_keys() -> None:

    memory = Memory()

    first = memory.add("one")
    second = memory.add("two")

    assert first != second
    assert first == "memory-0"
    assert second == "memory-1"


def test_memory_add_does_not_reuse_removed_key() -> None:

    memory = Memory()

    first = memory.add("one")

    assert memory.remove(first) is True

    second = memory.add("two")

    assert second != first
    assert second == "memory-1"


# ==========================================================
# Update
# ==========================================================


def test_memory_update() -> None:

    memory = Memory()

    memory.update(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )

    assert memory.get("a") == 1
    assert memory.get("b") == 2
    assert memory.get("c") == 3

    assert memory.writes == 3


def test_memory_update_requires_dict() -> None:

    memory = Memory()

    with pytest.raises(
        TypeError,
        match="values must be a dict",
    ):
        memory.update(
            [("a", 1)]
        )


# ==========================================================
# Get / Recall
# ==========================================================


def test_memory_get_missing_returns_none() -> None:

    memory = Memory()

    assert memory.get("missing") is None
    assert memory.reads == 1


def test_memory_get_default() -> None:

    memory = Memory()

    assert memory.get(
        "missing",
        "default",
    ) == "default"

    assert memory.reads == 1


def test_memory_recall_is_alias_for_get() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    assert memory.recall("key") == "value"
    assert memory.reads == 1


# ==========================================================
# Last
# ==========================================================


def test_memory_last() -> None:

    memory = Memory()

    memory.add("hello")

    assert memory.last() == "hello"


def test_memory_last_returns_latest_value() -> None:

    memory = Memory()

    memory.add("first")
    memory.add("second")
    memory.add("third")

    assert memory.last() == "third"


def test_memory_last_empty_returns_none() -> None:

    memory = Memory()

    assert memory.last() is None


# ==========================================================
# Search
# ==========================================================


def test_memory_search() -> None:

    memory = Memory()

    memory.add("python")
    memory.add("scios")

    result = memory.search(
        "python"
    )

    assert "python" in result


def test_memory_search_is_case_insensitive() -> None:

    memory = Memory()

    memory.store(
        "language",
        "Python",
    )

    result = memory.search(
        "PYTHON"
    )

    assert "Python" in result


def test_memory_search_matches_key() -> None:

    memory = Memory()

    memory.store(
        "python-language",
        "programming",
    )

    result = memory.search(
        "python"
    )

    assert result == [
        "programming"
    ]


def test_memory_search_matches_value() -> None:

    memory = Memory()

    memory.store(
        "language",
        "Python runtime",
    )

    result = memory.search(
        "runtime"
    )

    assert result == [
        "Python runtime"
    ]


def test_memory_search_no_match() -> None:

    memory = Memory()

    memory.add("python")

    assert memory.search(
        "quantum"
    ) == []


def test_memory_search_requires_string_query() -> None:

    memory = Memory()

    with pytest.raises(
        TypeError,
        match="query must be a string",
    ):
        memory.search(123)


# ==========================================================
# Exists
# ==========================================================


def test_memory_exists() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    assert memory.exists("key") is True
    assert memory.exists("missing") is False


def test_memory_contains_protocol() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    assert "key" in memory
    assert "missing" not in memory


# ==========================================================
# Remove
# ==========================================================


def test_memory_remove_existing() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    assert memory.remove("key") is True
    assert memory.exists("key") is False
    assert len(memory) == 0


def test_memory_remove_missing() -> None:

    memory = Memory()

    assert memory.remove(
        "missing"
    ) is False


# ==========================================================
# Clear
# ==========================================================


def test_memory_clear() -> None:

    memory = Memory()

    memory.store("a", 1)
    memory.store("b", 2)

    memory.clear()

    assert len(memory) == 0
    assert memory.keys() == []


def test_memory_clear_preserves_diagnostics() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    memory.get("key")

    writes = memory.writes
    reads = memory.reads

    memory.clear()

    assert memory.writes == writes
    assert memory.reads == reads


# ==========================================================
# Collection API
# ==========================================================


def test_memory_keys() -> None:

    memory = Memory()

    memory.store("a", 1)
    memory.store("b", 2)

    assert memory.keys() == [
        "a",
        "b",
    ]


def test_memory_values() -> None:

    memory = Memory()

    memory.store("a", 1)
    memory.store("b", 2)

    assert memory.values() == [
        1,
        2,
    ]


def test_memory_items() -> None:

    memory = Memory()

    memory.store("a", 1)
    memory.store("b", 2)

    assert memory.items() == [
        ("a", 1),
        ("b", 2),
    ]


# ==========================================================
# Snapshot
# ==========================================================


def test_memory_snapshot() -> None:

    memory = Memory()

    memory.store(
        "key",
        {
            "value": 42,
        },
    )

    snapshot = memory.snapshot()

    assert snapshot == {
        "key": {
            "value": 42,
        }
    }


def test_memory_snapshot_is_deep_copy() -> None:

    memory = Memory()

    memory.store(
        "key",
        {
            "nested": [
                1,
                2,
            ]
        },
    )

    snapshot = memory.snapshot()

    snapshot["key"]["nested"].append(3)

    assert memory.get(
        "key"
    ) == {
        "nested": [
            1,
            2,
        ]
    }


# ==========================================================
# Restore
# ==========================================================


def test_memory_restore() -> None:

    memory = Memory()

    memory.store(
        "original",
        1,
    )

    snapshot = {
        "restored": 2,
    }

    memory.restore(
        snapshot
    )

    assert memory.to_dict() == {
        "restored": 2,
    }


def test_memory_restore_is_deep_copy() -> None:

    memory = Memory()

    snapshot = {
        "key": {
            "items": [
                1,
                2,
            ]
        }
    }

    memory.restore(
        snapshot
    )

    snapshot["key"]["items"].append(3)

    assert memory.to_dict() == {
        "key": {
            "items": [
                1,
                2,
            ]
        }
    }


def test_memory_restore_requires_dict() -> None:

    memory = Memory()

    with pytest.raises(
        TypeError,
        match="snapshot must be a dict",
    ):
        memory.restore(
            ["invalid"]
        )


def test_memory_restore_preserves_diagnostics() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    memory.get("key")

    writes = memory.writes
    reads = memory.reads

    memory.restore(
        {
            "restored": True,
        }
    )

    assert memory.writes == writes
    assert memory.reads == reads


# ==========================================================
# Serialization
# ==========================================================


def test_memory_to_dict() -> None:

    memory = Memory()

    memory.store(
        "key",
        {
            "value": 42,
        },
    )

    result = memory.to_dict()

    assert result == {
        "key": {
            "value": 42,
        }
    }


def test_memory_to_dict_is_deep_copy() -> None:

    memory = Memory()

    memory.store(
        "key",
        {
            "nested": [
                1,
            ]
        },
    )

    result = memory.to_dict()

    result["key"]["nested"].append(2)

    assert memory.get(
        "key"
    ) == {
        "nested": [
            1,
        ]
    }


# ==========================================================
# Diagnostics
# ==========================================================


def test_memory_status() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    memory.get("key")

    status = memory.status()

    assert status["size"] == 1
    assert status["keys"] == ["key"]
    assert status["writes"] == 1
    assert status["reads"] == 1


def test_memory_status_is_snapshot() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    status = memory.status()

    status["keys"].clear()

    assert memory.status()["keys"] == [
        "key"
    ]


# ==========================================================
# Mapping Protocol
# ==========================================================


def test_memory_getitem() -> None:

    memory = Memory()

    memory.store(
        "key",
        "value",
    )

    assert memory["key"] == "value"


def test_memory_setitem() -> None:

    memory = Memory()

    memory["key"] = "value"

    assert memory["key"] == "value"
    assert memory.writes == 1


def test_memory_iteration() -> None:

    memory = Memory()

    memory.store("a", 1)
    memory.store("b", 2)

    assert list(memory) == [
        "a",
        "b",
    ]


# ==========================================================
# Representation
# ==========================================================


def test_memory_repr() -> None:

    memory = Memory()

    text = repr(memory)

    assert "Memory" in text
    assert "size=0" in text
    assert "writes=0" in text
    assert "reads=0" in text