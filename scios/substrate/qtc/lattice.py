"""
SciOS QTC Lattice
=================

Lattice abstraction for the SciOS Quantum Temporal Compression (QTC)
subsystem.

A lattice represents a partially ordered set (poset) supporting
join (least upper bound) and meet (greatest lower bound) operations.

Responsibilities
----------------
- Represent qualitative state spaces
- Partial-order reasoning
- Join / Meet operations
- Top / Bottom elements
- Lattice validation

This module provides the abstract lattice foundation used by QTC,
reasoning engines, and symbolic execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterable, TypeVar

__all__ = [
    "LatticeNode",
    "QTCLattice",
]

T = TypeVar("T")


# ==========================================================
# Node
# ==========================================================

@dataclass(slots=True, frozen=True)
class LatticeNode(Generic[T]):
    """
    Immutable lattice node.
    """

    value: T

    def __repr__(self) -> str:
        return f"LatticeNode({self.value!r})"


# ==========================================================
# Abstract Lattice
# ==========================================================

class QTCLattice(ABC, Generic[T]):
    """
    Abstract lattice.

    A lattice defines a partially ordered set supporting
    least upper bound (join) and greatest lower bound (meet).
    """

    # ------------------------------------------------------
    # Order
    # ------------------------------------------------------

    @abstractmethod
    def less_equal(
        self,
        left: LatticeNode[T],
        right: LatticeNode[T],
    ) -> bool:
        """
        Partial order relation.

        Returns
        -------
        True if left <= right.
        """

    # ------------------------------------------------------
    # Join
    # ------------------------------------------------------

    @abstractmethod
    def join(
        self,
        left: LatticeNode[T],
        right: LatticeNode[T],
    ) -> LatticeNode[T]:
        """
        Least upper bound.
        """

    # ------------------------------------------------------
    # Meet
    # ------------------------------------------------------

    @abstractmethod
    def meet(
        self,
        left: LatticeNode[T],
        right: LatticeNode[T],
    ) -> LatticeNode[T]:
        """
        Greatest lower bound.
        """

    # ------------------------------------------------------
    # Top / Bottom
    # ------------------------------------------------------

    @property
    @abstractmethod
    def top(self) -> LatticeNode[T]:
        """
        Greatest lattice element.
        """

    @property
    @abstractmethod
    def bottom(self) -> LatticeNode[T]:
        """
        Least lattice element.
        """

    # ------------------------------------------------------
    # Membership
    # ------------------------------------------------------

    @abstractmethod
    def contains(
        self,
        node: LatticeNode[T],
    ) -> bool:
        """
        Return True if node belongs to the lattice.
        """

    # ------------------------------------------------------
    # Iteration
    # ------------------------------------------------------

    @abstractmethod
    def nodes(self) -> Iterable[LatticeNode[T]]:
        """
        Iterate over lattice nodes.
        """

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    def validate(self) -> bool:
        """
        Validate lattice consistency.

        Future versions may verify:

        - antisymmetry
        - transitivity
        - reflexivity
        - join/meet closure
        """

        return True

    # ------------------------------------------------------

    def __contains__(
        self,
        node: LatticeNode[T],
    ) -> bool:

        return self.contains(node)
