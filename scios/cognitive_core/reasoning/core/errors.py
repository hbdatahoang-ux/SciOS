"""Errors for the Reasoning subsystem."""


class ReasoningError(Exception):
    """Base exception for reasoning failures."""


class ReasoningValidationError(ReasoningError):
    """Raised when a reasoning input violates a contract."""


__all__ = [
    "ReasoningError",
    "ReasoningValidationError",
]
