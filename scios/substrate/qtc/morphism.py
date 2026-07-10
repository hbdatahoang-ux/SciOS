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

The morphism framework serves as the mathematical foundation for
symbolic reasoning, temporal compression, and knowledge
transformations throughout SciOS.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

__all__ = [
    "MorphismMetadata",
    "QTCMorphism",
    "IdentityMorphism",
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

    A morphism maps objects from one symbolic domain into
    another while preserving essential structure.
    """

    def __init__(
        self,
        metadata: MorphismMetadata,
    ) -> None:

        self._metadata = metadata

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
        Compose this morphism with another morphism.

        (other ∘ self)
        """

        return CompositeMorphism(
            first=self,
            second=other,
        )

    # ------------------------------------------------------

    def __call__(
        self,
        value: S,
    ) -> T:

        self.validate(value)

        return self.map(value)

    # ------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}')"
        )


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

            )
        )

        self._first = first

        self._second = second

    def map(
        self,
        value: S,
    ) -> U:

        return self._second(

            self._first(value)

        )
