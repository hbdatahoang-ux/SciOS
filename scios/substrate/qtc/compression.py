"""
SciOS QTC Compression
=====================

Foundation abstraction for the SciOS Quantum Temporal Compression (QTC)
subsystem.

A compression transforms symbolic or temporal information into a
compact representation while preserving the information required for
future reasoning.

Design Principles
-----------------
- Immutable metadata
- Stateless compression algorithms
- Runtime independent
- Generic type-safe API
- Backward compatible
- Extensible by inheritance

Python 3.11+
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
    """Base class for compression errors."""


class CompressionValidationError(CompressionError):
    """Raised when an input sequence is invalid."""


class CompressionIntegrityError(CompressionError):
    """Raised when decompression verification fails."""


# ==========================================================
# Metadata
# ==========================================================


@dataclass(slots=True, frozen=True)
class CompressionMetadata:
    """
    Immutable compression metadata.
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
    Result returned by a compression algorithm.
    """

    data: C

    original_size: int

    compressed_size: int

    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def ratio(self) -> float:
        """
        Compression ratio.

        compressed_size / original_size
        """

        if self.original_size <= 0:
            return 1.0

        return self.compressed_size / self.original_size

    @property
    def compression_ratio(self) -> float:
        """
        Alias for ratio.
        """

        return self.ratio

    @property
    def saving(self) -> float:
        """
        Relative storage saving.
        """

        return 1.0 - self.ratio

    @property
    def saved(self) -> int:
        """
        Number of removed items.
        """

        return self.original_size - self.compressed_size

    def __len__(self) -> int:
        return self.compressed_size

    def __bool__(self) -> bool:
        return self.compressed_size > 0

    def __repr__(self) -> str:

        return (
            f"CompressionResult("
            f"original={self.original_size}, "
            f"compressed={self.compressed_size}, "
            f"ratio={self.ratio:.3f})"
        )


# ==========================================================
# Base Compression
# ==========================================================


class QTCCompression(ABC, Generic[T, C]):
    """
    Abstract compression algorithm.

    Compression implementations should remain stateless.
    """

    #
    # Backward compatibility.
    #
    result_type = CompressionResult

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
        return self._metadata

    @property
    def name(self) -> str:
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

        Subclasses may extend this implementation.
        """

        if sequence is None:
            raise CompressionValidationError(
                "Input sequence cannot be None."
            )

        if not isinstance(sequence, Sequence):
            raise CompressionValidationError(
                "Input must implement Sequence."
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
        Compress a sequence.
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
    # Backward Compatibility
    # ------------------------------------------------------

    def compress_into(
        self,
        sequence: Sequence[T],
    ) -> CompressionResult[C]:
        """
        Legacy alias for compress().
        """

        return self.compress(sequence)

    # ------------------------------------------------------
    # Verification
    # ------------------------------------------------------

    def verify(
        self,
        original: Sequence[T],
        restored: Sequence[T],
    ) -> bool:
        """
        Verify decompression integrity.

        Default implementation compares the
        restored sequence element-by-element.
        """

        return list(original) == list(restored)

    # ------------------------------------------------------
    # Callable
    # ------------------------------------------------------

    def __call__(
        self,
        sequence: Sequence[T],
    ) -> CompressionResult[C]:

        self.validate(sequence)

        return self.compress(sequence)

    # ------------------------------------------------------
    # Python Protocols
    # ------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"lossless={self.metadata.lossless}, "
            f"streaming={self.metadata.supports_streaming})"
        )

    def __str__(self) -> str:
        return self.name

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, QTCCompression):
            return NotImplemented

        return self.metadata == other.metadata

    def __hash__(self) -> int:
        return hash(self.metadata)