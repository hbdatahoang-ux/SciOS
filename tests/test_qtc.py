"""
SciOS QTC Tests
===============

Foundation tests for the Quantum Temporal Compression (QTC)
subsystem.

These tests validate the public API contracts of the QTC foundation
without depending on concrete implementations.
"""

from __future__ import annotations

import pytest

from scios.substrate.qtc.algebra import (
    AlgebraElement,
)

from scios.substrate.qtc.operator import (
    UnaryOperator,
    OperatorMetadata,
)

from scios.substrate.qtc.compression import (
    QTCCompression,
    CompressionMetadata,
)

from scios.substrate.qtc.morphism import (
    QTCMorphism,
    MorphismMetadata,
)


# ==========================================================
# Dummy Algebra
# ==========================================================


class DummyElement(AlgebraElement):

    def __init__(self, value):

        self.value = value


# ==========================================================
# Dummy Operator
# ==========================================================


class IdentityOperator(UnaryOperator):

    def __init__(self):

        super().__init__(
            OperatorMetadata(
                name="identity",
            )
        )

    def execute(
        self,
        operand,
    ):

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

    def __init__(self):

        super().__init__(
            CompressionMetadata(
                name="identity",
            )
        )

    def compress(
        self,
        sequence,
    ):

        return self.result_type(
            data=list(sequence),
            original_size=len(sequence),
            compressed_size=len(sequence),
        )

    def decompress(
        self,
        result,
    ):

        return result.data


# ==========================================================
# Dummy Morphism
# ==========================================================


class IdentityMorphism(
    QTCMorphism[
        DummyElement,
        DummyElement,
    ]
):

    def __init__(self):

        super().__init__(
            MorphismMetadata(
                name="identity",
            )
        )

    def apply(
        self,
        value,
    ):

        return value


# ==========================================================
# Algebra
# ==========================================================


def test_algebra_element():

    x = DummyElement(10)

    assert x.value == 10


# ==========================================================
# Operator
# ==========================================================


def test_operator():

    op = IdentityOperator()

    x = DummyElement(5)

    assert op(x) is x


def test_operator_metadata():

    op = IdentityOperator()

    assert op.name == "identity"

    assert op.metadata.version == "1.0"


# ==========================================================
# Compression
# ==========================================================


def test_compression():

    c = IdentityCompression()

    seq = [
        DummyElement(1),
        DummyElement(2),
    ]

    result = c.compress(seq)

    assert result.original_size == 2

    assert result.compressed_size == 2

    assert result.ratio == 1.0


def test_decompression():

    c = IdentityCompression()

    seq = [
        DummyElement(1),
    ]

    compressed = c.compress(seq)

    restored = c.decompress(compressed)

    assert len(restored) == 1


# ==========================================================
# Morphism
# ==========================================================


def test_morphism():

    m = IdentityMorphism()

    x = DummyElement(3)

    assert m(x) is x


def test_morphism_metadata():

    m = IdentityMorphism()

    assert m.name == "identity"


# ==========================================================
# Representation
# ==========================================================


def test_repr():

    op = IdentityOperator()

    assert "identity" in repr(op)


# ==========================================================
# Validation
# ==========================================================


def test_invalid_compression():

    c = IdentityCompression()

    with pytest.raises(Exception):

        c.compress(None)