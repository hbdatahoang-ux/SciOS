"""
SciOS QTC Algebra
=================

Qualitative algebra engine for the SciOS Qualitative
Temporal Calculus (QTC).

Responsibilities
----------------
- Qualitative relation definitions
- Relation composition
- Inverse relations
- Identity relation
- Algebra validation
- Symbolic reasoning primitives
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet

__all__ = [
    "QTCRelation",
    "QTCAlgebra",
]


# ==========================================================
# Relations
# ==========================================================

class QTCRelation(str, Enum):
    """
    Fundamental qualitative relations.

    Initial relation set.
    Can be extended by future QTC variants.
    """

    EQUAL = "="

    BEFORE = "<"

    AFTER = ">"

    UNKNOWN = "?"


# ==========================================================
# Algebra
# ==========================================================

@dataclass(slots=True)
class QTCAlgebra:
    """
    Qualitative algebra.

    Encapsulates relation composition,
    inverse computation and validation.
    """

    composition: Dict[
        tuple[QTCRelation, QTCRelation],
        FrozenSet[QTCRelation],
    ]

    inverse: Dict[
        QTCRelation,
        QTCRelation,
    ]

    identity: QTCRelation = QTCRelation.EQUAL

    # ======================================================
    # Composition
    # ======================================================

    def compose(
        self,
        left: QTCRelation,
        right: QTCRelation,
    ) -> FrozenSet[QTCRelation]:
        """
        Compose two qualitative relations.
        """

        return self.composition.get(
            (left, right),
            frozenset(
                {QTCRelation.UNKNOWN}
            ),
        )

    # ======================================================
    # Inverse
    # ======================================================

    def invert(
        self,
        relation: QTCRelation,
    ) -> QTCRelation:
        """
        Return inverse relation.
        """

        return self.inverse.get(
            relation,
            QTCRelation.UNKNOWN,
        )

    # ======================================================
    # Identity
    # ======================================================

    def is_identity(
        self,
        relation: QTCRelation,
    ) -> bool:
        """
        Check identity relation.
        """

        return relation == self.identity

    # ======================================================
    # Validation
    # ======================================================

    def validate(self) -> bool:
        """
        Validate algebra consistency.

        Future versions may verify:

        - closure
        - associativity
        - inverse consistency
        - identity laws
        """

        return True

    # ======================================================
    # Factory
    # ======================================================

    @classmethod
    def default(cls) -> "QTCAlgebra":
        """
        Default minimal algebra.
        """

        composition = {

            (
                QTCRelation.EQUAL,
                QTCRelation.EQUAL,
            ): frozenset(
                {QTCRelation.EQUAL}
            ),

            (
                QTCRelation.BEFORE,
                QTCRelation.BEFORE,
            ): frozenset(
                {QTCRelation.BEFORE}
            ),

            (
                QTCRelation.AFTER,
                QTCRelation.AFTER,
            ): frozenset(
                {QTCRelation.AFTER}
            ),
        }

        inverse = {

            QTCRelation.EQUAL:
                QTCRelation.EQUAL,

            QTCRelation.BEFORE:
                QTCRelation.AFTER,

            QTCRelation.AFTER:
                QTCRelation.BEFORE,

            QTCRelation.UNKNOWN:
                QTCRelation.UNKNOWN,
        }

        return cls(

            composition=composition,

            inverse=inverse,
        )

    # ======================================================

    def __repr__(self) -> str:

        return (

            "QTCAlgebra("

            f"relations={len(QTCRelation)})"

        )
