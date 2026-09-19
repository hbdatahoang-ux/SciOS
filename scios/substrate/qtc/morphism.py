"""
SciOS QTC Morphism
==================

Foundation morphism abstraction for the SciOS Quantum Temporal
Compression (QTC) subsystem.

A morphism represents a structure-preserving transformation between
two symbolic domains.

Responsibilities
----------------
- Symbolic transformations
- Structure preservation
- Composition
- Identity morphisms
- Morphism validation

Python 3.11+
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

__all__ = [
    "MorphismMetadata",
    "QTCMorphism",
    "IdentityMorphism",
    "CompositeMorphism",
]

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")


# ==========================================================
# Metadata
# ==========================================================


@dataclass(slots=True, frozen=True)
class MorphismMetadata:
    """
    Immutable metadata describing a morphism.
    """

    name: str

    version: str = "1.0"

    description: str = ""

    invertible: bool = False

    deterministic: bool = True


# ==========================================================
# Base Morphism
# ==========================================================


class QTCMorphism(ABC, Generic[S, T]):
    """
    Abstract structure-preserving mapping.
    """

    def __init__(
        self,
        metadata: MorphismMetadata,
    ) -> None:

        self._metadata = metadata

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    @property
    def metadata(self) -> MorphismMetadata:
        return self._metadata

    @property
    def name(self) -> str:
        return self._metadata.name

    # ------------------------------------------------------
    # Core Mapping
    # ------------------------------------------------------

    @abstractmethod
    def map(
        self,
        value: S,
    ) -> T:
        """
        Apply the morphism.
        """

    # ------------------------------------------------------
    # Backward Compatibility
    # ------------------------------------------------------

    def apply(
        self,
        value: S,
    ) -> T:
        """
        Backward-compatible alias.

        Older SciOS releases exposed apply()
        instead of map().
        """

        return self.map(value)

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    def validate(
        self,
        value: S,
    ) -> bool:
        """
        Validate an input value.

        Subclasses may override.
        """

        return True

    # ------------------------------------------------------
    # Composition
    # ------------------------------------------------------

    def compose(
        self,
        other: "QTCMorphism[T, U]",
    ) -> "QTCMorphism[S, U]":
        """
        Compose two morphisms.

        Result:

            other ∘ self
        """

        return CompositeMorphism(
            first=self,
            second=other,
        )

    # ------------------------------------------------------
    # Callable
    # ------------------------------------------------------

    def __call__(
        self,
        value: S,
    ) -> T:

        self.validate(value)

        return self.map(value)

    # ------------------------------------------------------
    # Python Protocols
    # ------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}')"
        )

    def __str__(self) -> str:
        return self.name

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, QTCMorphism):
            return NotImplemented

        return self.metadata == other.metadata

    def __hash__(self) -> int:
        return hash(self.metadata)


# ==========================================================
# Identity Morphism
# ==========================================================


class IdentityMorphism(QTCMorphism[S, S]):
    """
    Identity morphism.

    f(x) = x
    """

    def __init__(self) -> None:

        super().__init__(
            MorphismMetadata(
                name="identity",
                description="Identity morphism",
                invertible=True,
            )
        )

    def map(
        self,
        value: S,
    ) -> S:

        return value


# ==========================================================
# Composite Morphism
# ==========================================================


class CompositeMorphism(QTCMorphism[S, U]):
    """
    Composition of two morphisms.

    h = g ∘ f
    """

    def __init__(
        self,
        first: QTCMorphism[S, T],
        second: QTCMorphism[T, U],
    ) -> None:

        super().__init__(
            MorphismMetadata(
                name=f"{second.name}∘{first.name}",
                description="Composite morphism",
                invertible=(
                    first.metadata.invertible
                    and second.metadata.invertible
                ),
                deterministic=(
                    first.metadata.deterministic
                    and second.metadata.deterministic
                ),
            )
        )

        self._first = first
        self._second = second

    @property
    def first(self) -> QTCMorphism[S, T]:
        return self._first

    @property
    def second(self) -> QTCMorphism[T, U]:
        return self._second

    def map(
        self,
        value: S,
    ) -> U:

        return self._second(
            self._first(value)
        )