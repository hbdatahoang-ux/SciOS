"""
SciOS Vector Store Benchmarks

Run:

pytest benchmarks/benchmark_vectorstore.py --benchmark-only
"""

from __future__ import annotations

import random

import pytest

from scios.substrate.vectorstore.storage import (
    VectorRecord,
    VectorStore,
)


DIMENSION = 128
NUM_VECTORS = 1_000


def make_vector() -> list[float]:
    return [random.random() for _ in range(DIMENSION)]


@pytest.fixture
def store() -> VectorStore:
    vector_store = VectorStore(dimension=DIMENSION)

    for i in range(NUM_VECTORS):
        vector_store.add(
            f"doc-{i}",
            make_vector(),
        )

    return vector_store


@pytest.fixture
def query_vector() -> list[float]:
    return make_vector()


def test_vectorstore_creation(benchmark):
    """
    Benchmark VectorStore construction.
    """
    benchmark(
        VectorStore,
        dimension=DIMENSION,
    )


def test_vectorstore_insert(benchmark):
    """
    Benchmark single vector insertion.
    """
    vector_store = VectorStore(
        dimension=DIMENSION,
    )

    vector = [0.5] * DIMENSION

    benchmark(
        vector_store.add,
        "sample",
        vector,
    )


def test_vectorstore_search(
    store,
    query_vector,
    benchmark,
):
    """
    Benchmark top-k cosine similarity search.
    """
    benchmark(
        store.search,
        query_vector,
        10,
    )


def test_vectorstore_update(
    store,
    benchmark,
):
    """
    Benchmark VectorRecord replacement.
    """
    record = VectorRecord(
        id="doc-1",
        vector=store.get_record("doc-1").vector,
        metadata=store.get_record("doc-1").metadata,
    )

    benchmark(
        store.update,
        record,
    )


def test_vectorstore_delete(
    store,
    benchmark,
):
    """
    Benchmark vector deletion.
    """
    benchmark(
        store.delete,
        "doc-1",
    )


def test_vectorstore_bulk_insert(benchmark):
    """
    Benchmark bulk VectorRecord insertion.
    """
    vector_store = VectorStore(
        dimension=DIMENSION,
    )

    records = [
        VectorRecord(
            id=f"doc-{i}",
            vector=vector_store._normalize_vector(
                make_vector()
            ),
            metadata=vector_store.values()[0].metadata
            if vector_store.values()
            else __import__(
                "scios.substrate.vectorstore.metadata",
                fromlist=["Metadata"],
            ).Metadata(),
        )
        for i in range(NUM_VECTORS)
    ]

    benchmark(
        vector_store.add_many,
        records,
    )