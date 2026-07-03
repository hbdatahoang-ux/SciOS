"""
SciOS QTC Operator Framework
============================

Foundation operator abstraction for the SciOS Quantum Temporal
Compression (QTC) subsystem.

The operator framework defines the execution contract shared by all
symbolic operators within SciOS.

Architecture
------------
QTCAlgebra
      │
      ▼
QTCOperator (abstract)
      │
 ┌────┼────┐
 ▼    ▼    ▼
Unary Binary N-ary
      │
      ▼
Concrete Operators
      │
      ▼
Kernel Runtime

Design Principles
-----------------
- Stable public API
- Stateless execution
- Immutable metadata
- Runtime-independent
- Extensible by inheritance
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = [
    "OperatorArity",
    "OperatorMetadata",
    "QTCOperator",
    "UnaryOperator",
    "BinaryOperator",
    "NaryOperator",
]


# ==========================================================
# Operator Arity
# ==========================================================

class OperatorArity(str, Enum):
    """
    Number of operands accepted by an operator.
    """

    UNARY = "unary"

    BINARY = "binary"

    NARY = "nary"


# ==========================================================
# Operator Metadata
# ==========================================================

@dataclass(slots=True, frozen=True)
class OperatorMetadata:
    """
    Immutable metadata describing a QTC operator.
    """

    name: str

    version: str = "1.0"

    description: str = ""

    deterministic: bool = True

    differentiable: bool = False

    tags: tuple[str, ...] = field(default_factory=tuple)


# ==========================================================
# Base Operator
# ==========================================================

class QTCOperator(ABC):
    """
    Abstract base class for every QTC operator.

    Operators should be stateless.
    Runtime state must be provided through
    the execution context.
    """

    arity: OperatorArity

    def __init__(
        self,
        metadata: OperatorMetadata,
    ) -> None:

        self._metadata = metadata

    # ------------------------------------------------------

    @property
    def metadata(self) -> OperatorMetadata:
        """
        Immutable operator metadata.
        """
        return self._metadata

    @property
    def name(self) -> str:
        """
        Operator name.
        """
        return self._metadata.name

    # ------------------------------------------------------

    def validate(
        self,
        *operands: Any,
    ) -> None:
        """
        Validate operands before execution.

        Subclasses may override.
        """
        return None

    # ------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        context: Any | None,
        *operands: Any,
    ) -> Any:
        """
        Execute operator.

        Parameters
        ----------
        context
            Runtime execution context.

        operands
            Input operands.

        Returns
        -------
        Any
            Operator result.
        """

    # ------------------------------------------------------

    def __call__(
        self,
        *operands: Any,
        context: Any | None = None,
    ) -> Any:
        """
        Callable interface.
        """

        self.validate(*operands)

        return self.execute(
            context,
            *operands,
        )

    # ------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"arity='{self.arity.value}')"
        )


# ==========================================================
# Unary Operator
# ==========================================================

class UnaryOperator(QTCOperator):
    """
    Base class for unary operators.
    """

    arity = OperatorArity.UNARY

    @abstractmethod
    def execute(
        self,
        context: Any | None,
        operand: Any,
    ) -> Any:
        ...


# ==========================================================
# Binary Operator
# ==========================================================

class BinaryOperator(QTCOperator):
    """
    Base class for binary operators.
    """

    arity = OperatorArity.BINARY

    @abstractmethod
    def execute(
        self,
        context: Any | None,
        left: Any,
        right: Any,
    ) -> Any:
        ...


# ==========================================================
# N-ary Operator
# ==========================================================

class NaryOperator(QTCOperator):
    """
    Base class for operators accepting an arbitrary
    number of operands.
    """

    arity = OperatorArity.NARY

    @abstractmethod
    def execute(
        self,
        context: Any | None,
        *operands: Any,
    ) -> Any:
        ...