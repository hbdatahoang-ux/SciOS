"""
SciOS Vector Store Benchmarks

Run:

pytest benchmarks/benchmark_vectorstore.py \
    --benchmark-only
"""

from __future__ import annotations

import random

import pytest

from scios.substrate.vectorstore.index import VectorIndex


DIMENSION = 128
NUM_VECTORS = 1_000


@pytest.fixture
def index() -> VectorIndex:
    idx = VectorIndex(dimension=DIMENSION)

    for i in range(NUM_VECTORS):
        vector = [random.random() for _ in range(DIMENSION)]
        idx.add(f"doc-{i}", vector)

    return idx


@pytest.fixture
def query_vector():
    return [random.random() for _ in range(DIMENSION)]


def test_vectorstore_creation(benchmark):
    """
    Benchmark index construction.
    """
    benchmark(VectorIndex, dimension=DIMENSION)


def test_vectorstore_insert(benchmark):
    """
    Benchmark single vector insertion.
    """

    idx = VectorIndex(dimension=DIMENSION)
    vector = [0.5] * DIMENSION

    benchmark(idx.add, "sample", vector)


def test_vectorstore_search(index, query_vector, benchmark):
    """
    Benchmark top-k search.
    """

    benchmark(
        index.search,
        query_vector,
        10,
    )


def test_vectorstore_update(index, benchmark):
    """
    Benchmark vector replacement.
    """

    vector = [0.8] * DIMENSION

    benchmark(
        index.update,
        "doc-1",
        vector,
    )


def test_vectorstore_delete(index, benchmark):
    """
    Benchmark vector deletion.
    """

    benchmark(
        index.delete,
        "doc-1",
    )


def test_vectorstore_bulk_insert(benchmark):
    """
    Benchmark bulk insertion.
    """

    idx = VectorIndex(dimension=DIMENSION)

    vectors = [
        (
            f"doc-{i}",
            [random.random() for _ in range(DIMENSION)]
        )
        for i in range(NUM_VECTORS)
    ]

    def workload():

        for key, vector in vectors:
            idx.add(key, vector)

    benchmark(workload)