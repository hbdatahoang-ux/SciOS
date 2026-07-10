"""
SciOS QTC Benchmarks

Run:

pytest benchmarks/benchmark_qtc.py \
    --benchmark-only
"""

from __future__ import annotations

import pytest

from scios.substrate.qtc.algebra import Algebra
from scios.substrate.qtc.operator import Operator
from scios.substrate.qtc.morphism import Morphism
from scios.substrate.qtc.compression import Compression


@pytest.fixture
def algebra():
    return Algebra()


@pytest.fixture
def operator():
    return Operator()


@pytest.fixture
def morphism():
    return Morphism()


@pytest.fixture
def compression():
    return Compression()


@pytest.fixture
def sample_state():
    return {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
    }


def test_algebra_creation(benchmark):
    """
    Benchmark Algebra construction.
    """
    benchmark(Algebra)


def test_operator_apply(operator, sample_state, benchmark):
    """
    Benchmark Operator.apply().
    """
    benchmark(operator.apply, sample_state)


def test_algebra_compose(algebra, benchmark):
    """
    Benchmark Algebra.compose().
    """
    benchmark(algebra.compose)


def test_morphism_transform(morphism, sample_state, benchmark):
    """
    Benchmark Morphism.transform().
    """
    benchmark(
        morphism.transform,
        sample_state,
    )


def test_compression(compression, sample_state, benchmark):
    """
    Benchmark Compression.compress().
    """
    benchmark(
        compression.compress,
        sample_state,
    )


def test_qtc_pipeline(
    algebra,
    operator,
    morphism,
    compression,
    sample_state,
    benchmark,
):
    """
    Benchmark complete QTC pipeline.
    """

    def workload():

        state = operator.apply(sample_state)

        state = morphism.transform(state)

        state = compression.compress(state)

        algebra.compose()

    benchmark(workload)
