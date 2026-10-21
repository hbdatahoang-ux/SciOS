from __future__ import annotations

from scios.substrate.qtc.algebra import QTCAlgebra, QTCRelation
from scios.substrate.qtc.morphism import (
    CompositeMorphism,
    IdentityMorphism,
)


def test_benchmark_qtc_algebra_compose(benchmark) -> None:
    algebra = QTCAlgebra.default()

    benchmark(
        algebra.compose,
        QTCRelation.BEFORE,
        QTCRelation.BEFORE,
    )


def test_benchmark_qtc_algebra_invert(benchmark) -> None:
    algebra = QTCAlgebra.default()

    benchmark(
        algebra.invert,
        QTCRelation.BEFORE,
    )


def test_benchmark_qtc_algebra_identity(benchmark) -> None:
    algebra = QTCAlgebra.default()

    benchmark(
        algebra.is_identity,
        QTCRelation.EQUAL,
    )


def test_benchmark_qtc_algebra_validate(benchmark) -> None:
    algebra = QTCAlgebra.default()

    benchmark(algebra.validate)


def test_benchmark_qtc_identity_morphism(benchmark) -> None:
    morphism = IdentityMorphism()
    value = object()

    benchmark(morphism.map, value)


def test_benchmark_qtc_identity_morphism_call(benchmark) -> None:
    morphism = IdentityMorphism()
    value = object()

    benchmark(morphism, value)


def test_benchmark_qtc_composite_morphism(benchmark) -> None:
    first = IdentityMorphism()
    second = IdentityMorphism()
    composite = CompositeMorphism(first, second)

    value = object()

    benchmark(composite.map, value)
