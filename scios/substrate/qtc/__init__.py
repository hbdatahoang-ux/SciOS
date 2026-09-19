"""
SciOS QTC
=========

Qualitative Temporal Calculus (QTC) subsystem.

The QTC subsystem provides the symbolic mathematical foundation
for qualitative spatial-temporal reasoning within SciOS.

Architecture
------------
QTC
├── Algebra
├── Operators
├── Lattice
├── Morphisms
└── Compression

Responsibilities
----------------
- Symbolic qualitative reasoning
- Spatial-temporal algebra
- State lattice representation
- Structural morphisms
- Temporal sequence compression

Public API
----------
QTCAlgebra
    Qualitative algebra and composition rules.

QTCOperator
    Base class for qualitative operators.

QTCLattice
    Lattice representation of qualitative states.

QTCMorphism
    Structure-preserving mappings between QTC spaces.

QTCCompression
    Symbolic temporal sequence compression.
"""

from .algebra import QTCAlgebra
from .operator import QTCOperator
from .lattice import QTCLattice
from .morphism import QTCMorphism
from .compression import QTCCompression

__all__ = [
    "QTCAlgebra",
    "QTCOperator",
    "QTCLattice",
    "QTCMorphism",
    "QTCCompression",
]
