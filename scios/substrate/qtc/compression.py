"""
SciOS QTC Compression
=====================

Foundation abstraction for the Quantum Temporal Compression (QTC)
subsystem.

A compression transforms symbolic or temporal information into a
compact representation while preserving the information required for
future reasoning.

This module defines the stable public API for every compression
algorithm implemented in SciOS.

Design Principles
-----------------
- Immutable metadata
- Stateless compression algorithms
- Runtime independent
- Generic type-safe API
- Extensible by inheritance
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Mapping, Sequence, TypeVar

__all__ = [
    "CompressionMetadata",
    "CompressionResult",
    "CompressionError",
    "CompressionValidationError",
    "CompressionIntegrityError",
    "QTCCompression",
]

T = TypeVar("T")
C = TypeVar("C")


# ==========================================================
# Exceptions
# ==========================================================


class CompressionError(Exception):
    """
    Base class for all compression errors.
    """


class CompressionValidationError(CompressionError):
    """
    Invalid input sequence.
    """


class CompressionIntegrityError(CompressionError):
    """
    Decompressed data failed integrity validation.
    """


# ==========================================================
# Metadata
# ==========================================================


@dataclass(slots=True, frozen=True)
class CompressionMetadata:
    """
    Immutable metadata describing a compression algorithm.
    """

    name: str

    version: str = "1.0"

    description: str = ""

    lossless: bool = True

    deterministic: bool = True

    supports_streaming: bool = False

    supports_parallel: bool = False


# ==========================================================
# Compression Result
# ==========================================================


@dataclass(slots=True, frozen=True)
class CompressionResult(Generic[C]):
    """
    Result produced by a compression algorithm.
    """

    data: C

    original_size: int

    compressed_size: int

    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def ratio(self) -> float:
        """
        Compression ratio.

        Returns
        -------
        compressed_size / original_size
        """

        if self.original_size <= 0:
            return 1.0

        return self.compressed_size / self.original_size

    @property
    def saving(self) -> float:
        """
        Relative storage saving.
        """

        return 1.0 - self.ratio

    @property
    def saved(self) -> int:
        """
        Number of removed elements.
        """

        return self.original_size - self.compressed_size

    def __len__(self) -> int:
        return self.compressed_size

    def __bool__(self) -> bool:
        return self.compressed_size > 0


# ==========================================================
# Base Compression
# ==========================================================


class QTCCompression(ABC, Generic[T, C]):
    """
    Abstract compression algorithm.

    Implementations should be stateless.

    Runtime state, caches, devices, schedulers and execution
    policies belong to higher layers of SciOS.
    """

    def __init__(
        self,
        metadata: CompressionMetadata,
    ) -> None:

        self._metadata = metadata

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    @property
    def metadata(self) -> CompressionMetadata:
        """
        Immutable algorithm metadata.
        """

        return self._metadata

    @property
    def name(self) -> str:
        """
        Algorithm name.
        """

        return self._metadata.name

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    def validate(
        self,
        sequence: Sequence[T],
    ) -> None:
        """
        Validate an input sequence.

        Subclasses may override.
        """

        if sequence is None:
            raise CompressionValidationError(
                "Input sequence cannot be None."
            )

    # ------------------------------------------------------
    # Core API
    # ------------------------------------------------------

    @abstractmethod
    def compress(
        self,
        sequence: Sequence[T],
    ) -> CompressionResult[C]:
        """
        Compress an input sequence.
        """

    @abstractmethod
    def decompress(
        self,
        result: CompressionResult[C],
    ) -> Sequence[T]:
        """
        Restore the original sequence.
        """

    # ------------------------------------------------------
    # Optional Verification
    # ------------------------------------------------------

    def verify(
        self,
        original: Sequence[T],
        restored: Sequence[T],
    ) -> bool:
        """
        Verify decompression integrity.

        Default implementation performs equality comparison.
        """

        return list(original) == list(restored)

    # ------------------------------------------------------
    # Callable Interface
    # ------------------------------------------------------

    def __call__(
        self,
        sequence: Sequence[T],
    ) -> CompressionResult[C]:

        self.validate(sequence)

        return self.compress(sequence)

    # ------------------------------------------------------
    # Representation
    # ------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"lossless={self.metadata.lossless}, "
            f"streaming={self.metadata.supports_streaming})"
        )
