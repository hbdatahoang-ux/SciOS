"""
SciOS Vector Store Tests
========================

Foundation tests for the SciOS Vector Store subsystem.

These tests validate the stable public API without depending on a
specific backend implementation.
"""

from __future__ import annotations

import pytest

from scios.substrate.vectorstore.storage import VectorStore


# ==========================================================
# Construction
# ==========================================================

def test_vectorstore_construction() -> None:
    """
    Vector store should be constructible.
    """

    store = VectorStore(dimension=3)

    assert store is not None


# ==========================================================
# Initial State
# ==========================================================

def test_vectorstore_initially_empty() -> None:
    """
    Newly created vector store should be empty.
    """

    store = VectorStore(dimension=3)

    assert len(store) == 0
    assert store.empty()


# ==========================================================
# Add Vector
# ==========================================================

def test_add_vector() -> None:
    """
    Vectors should be insertable.
    """

    store = VectorStore(dimension=3)

    store.add(
        id="a",
        vector=[1.0, 0.0, 0.0],
    )

    assert len(store) == 1


# ==========================================================
# Retrieve Vector
# ==========================================================

def test_get_vector() -> None:
    """
    Stored vectors should be retrievable.
    """

    store = VectorStore(dimension=3)

    store.add(
        id="x",
        vector=[1.0, 2.0, 3.0],
    )

    vector = store.get("x")

    assert vector == [1.0, 2.0, 3.0]


# ==========================================================
# Exists
# ==========================================================

def test_exists() -> None:
    """
    Membership queries should work.
    """

    store = VectorStore(dimension=3)

    store.add(
        id="v",
        vector=[1, 0, 0],
    )

    assert store.exists("v")
    assert not store.exists("missing")


# ==========================================================
# Remove
# ==========================================================

def test_remove_vector() -> None:
    """
    Removing vectors should succeed.
    """

    store = VectorStore(dimension=3)

    store.add(
        id="v",
        vector=[1, 2, 3],
    )

    store.remove("v")

    assert not store.exists("v")


# ==========================================================
# Similarity Search
# ==========================================================

def test_similarity_search() -> None:
    """
    Similarity search should return at least one result.
    """

    store = VectorStore(dimension=3)

    store.add("a", [1, 0, 0])
    store.add("b", [0, 1, 0])

    results = store.search(
        [1, 0, 0],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].id == "a"


# ==========================================================
# Clear
# ==========================================================

def test_clear() -> None:
    """
    Clearing should remove all vectors.
    """

    store = VectorStore(dimension=3)

    store.add("a", [1, 0, 0])
    store.add("b", [0, 1, 0])

    store.clear()

    assert len(store) == 0
    assert store.empty()


# ==========================================================
# Invalid Dimension
# ==========================================================

def test_invalid_dimension() -> None:
    """
    Invalid vector dimensions should raise an exception.
    """

    store = VectorStore(dimension=3)

    with pytest.raises(Exception):

        store.add(
            "bad",
            [1, 2],
        )


# ==========================================================
# Duplicate ID
# ==========================================================

def test_duplicate_id() -> None:
    """
    Existing IDs should be replaceable.
    """

    store = VectorStore(dimension=3)

    store.add(
        "x",
        [1, 0, 0],
    )

    store.add(
        "x",
        [2, 0, 0],
    )

    assert store.get("x") == [2, 0, 0]


# ==========================================================
# Multiple Insertions
# ==========================================================

def test_many_vectors() -> None:
    """
    Store should handle many vectors.
    """

    store = VectorStore(dimension=8)

    for i in range(100):

        store.add(
            str(i),
            [float(i)] * 8,
        )

    assert len(store) == 100


# ==========================================================
# Status
# ==========================================================

def test_status_schema() -> None:
    """
    Status should expose a stable schema.
    """

    store = VectorStore(dimension=16)

    status = store.status()

    required = {
        "dimension",
        "size",
    }

    assert required.issubset(status.keys())


# ==========================================================
# Iteration
# ==========================================================

def test_iteration() -> None:
    """
    Store should be iterable.
    """

    store = VectorStore(dimension=3)

    store.add("a", [1, 0, 0])
    store.add("b", [0, 1, 0])

    ids = {item.id for item in store}

    assert ids == {"a", "b"}
