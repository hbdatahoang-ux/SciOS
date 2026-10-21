"""Core types for the Reasoning subsystem."""

from enum import Enum


class ReasoningType(str, Enum):
    """Supported reasoning modes."""

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"


__all__ = [
    "ReasoningType",
]
