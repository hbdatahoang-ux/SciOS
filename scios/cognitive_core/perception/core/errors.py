"""Errors for the SciOS Cognitive Core Perception subsystem."""

from __future__ import annotations


class PerceptionError(Exception):
    """Base exception for all perception-related errors."""


class PerceptionInputError(PerceptionError):
    """Raised when perception input is invalid."""


class PerceptionConfigurationError(PerceptionError):
    """Raised when perception configuration is invalid."""


class PerceptionProcessingError(PerceptionError):
    """Raised when perception processing fails."""


class PerceptionValidationError(PerceptionError):
    """Raised when a perception result fails validation."""


__all__ = [
    "PerceptionConfigurationError",
    "PerceptionError",
    "PerceptionInputError",
    "PerceptionProcessingError",
    "PerceptionValidationError",
]
