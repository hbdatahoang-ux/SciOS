"""
SciOS QTC Tests
===============

Foundation tests for the SciOS Quantum Temporal Compression (QTC)
subsystem.

These tests validate the public API contracts of the QTC foundation
without depending on concrete implementations.

Python 3.11+
"""

from __future__ import annotations

from typing import Any

import pytest

from scios.substrate.qtc.algebra import AlgebraElement
from scios.substrate.qtc.operator import (
    OperatorMetadata,
    UnaryOperator,
)
from scios.substrate.qtc.compression import (
    CompressionMetadata,
    CompressionResult,
    CompressionValidationError,
    QTCCompression,
)
from scios.substrate.qtc.morphism import (
    MorphismMetadata,
    QTCMorphism,
)


# ==========================================================
# Dummy Algebra
# ==========================================================


class DummyElement(AlgebraElement):
    """Minimal algebra element used for testing."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DummyElement):
            return NotImplemented
        return self.value == other.value

    def __repr__(self) -> str:
        return f"DummyElement({self.value})"


# ==========================================================
# Dummy Operator
# ==========================================================


class IdentityOperator(UnaryOperator):
    """Identity operator."""

    def __init__(self) -> None:
        super().__init__(
            OperatorMetadata(
                name="identity",
            )
        )

    def execute(
        self,
        context: Any | None,
        operand: DummyElement,
    ) -> DummyElement:
        return operand


# ==========================================================
# Dummy Compression
# ==========================================================


class IdentityCompression(
    QTCCompression[
        DummyElement,
        list[DummyElement],
    ]
):
    """Identity compression."""

    def __init__(self) -> None:
        super().__init__(
            CompressionMetadata(
                name="identity",
            )
        )

    def compress(
        self,
        sequence,
    ) -> CompressionResult[list[DummyElement]]:

        self.validate(sequence)

        return CompressionResult(
            data=list(sequence),
            original_size=len(sequence),
            compressed_size=len(sequence),
        )

    def decompress(
        self,
        result: CompressionResult[list[DummyElement]],
    ) -> list[DummyElement]:

        return list(result.data)


# ==========================================================
# Dummy Morphism
# ==========================================================


class IdentityMorphism(
    QTCMorphism[
        DummyElement,
        DummyElement,
    ]
):
    """Identity morphism."""

    def __init__(self) -> None:
        super().__init__(
            MorphismMetadata(
                name="identity",
            )
        )

    def map(
        self,
        value: DummyElement,
    ) -> DummyElement:
        return value


# ==========================================================
# Algebra
# ==========================================================


def test_algebra_element() -> None:

    x = DummyElement(10)

    assert x.value == 10

    assert repr(x) == "DummyElement(10)"


# ==========================================================
# Operator
# ==========================================================


def test_operator() -> None:

    op = IdentityOperator()

    x = DummyElement(5)

    assert op(x) is x


def test_operator_metadata() -> None:

    op = IdentityOperator()

    assert op.name == "identity"

    assert op.metadata.name == "identity"

    assert op.metadata.version == "1.0"

    assert op.metadata.deterministic is True

    assert op.metadata.differentiable is False


def test_operator_repr() -> None:

    text = repr(
        IdentityOperator()
    )

    assert "IdentityOperator" in text

    assert "identity" in text

    assert "unary" in text


# ==========================================================
# Compression
# ==========================================================


def test_compression() -> None:

    c = IdentityCompression()

    seq = [
        DummyElement(1),
        DummyElement(2),
    ]

    result = c.compress(seq)

    assert isinstance(
        result,
        CompressionResult,
    )

    assert result.original_size == 2

    assert result.compressed_size == 2

    assert result.saved == 0

    assert result.ratio == 1.0

    assert result.saving == 0.0

    assert bool(result)

    assert len(result) == 2


def test_decompression() -> None:

    c = IdentityCompression()

    seq = [
        DummyElement(1),
    ]

    compressed = c.compress(seq)

    restored = c.decompress(compressed)

    assert restored == seq


def test_verify() -> None:

    c = IdentityCompression()

    seq = [
        DummyElement(1),
        DummyElement(2),
    ]

    restored = c.decompress(
        c.compress(seq)
    )

    assert c.verify(
        seq,
        restored,
    )


def test_callable_compression() -> None:

    c = IdentityCompression()

    seq = [
        DummyElement(1),
    ]

    result = c(seq)

    assert isinstance(
        result,
        CompressionResult,
    )


def test_invalid_compression() -> None:

    c = IdentityCompression()

    with pytest.raises(
        CompressionValidationError,
    ):
        c(None)


# ==========================================================
# Morphism
# ==========================================================


def test_morphism() -> None:

    m = IdentityMorphism()

    x = DummyElement(3)

    assert m(x) is x


def test_morphism_apply_alias() -> None:

    m = IdentityMorphism()

    x = DummyElement(7)

    assert m.apply(x) is x


def test_morphism_metadata() -> None:

    m = IdentityMorphism()

    assert m.name == "identity"

    assert m.metadata.name == "identity"

    assert m.metadata.version == "1.0"

    assert m.metadata.deterministic is True


def test_morphism_repr() -> None:

    text = repr(
        IdentityMorphism()
    )

    assert "IdentityMorphism" in text

    assert "identity" in text