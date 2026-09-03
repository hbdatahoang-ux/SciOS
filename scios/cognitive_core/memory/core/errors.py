from __future__ import annotations


class MemoryError(Exception):
    """Base exception for all memory subsystem errors."""


class MemoryValidationError(MemoryError):
    """Raised when memory input or state violates the contract."""


class MemoryNotFoundError(MemoryError):
    """Raised when a requested memory record does not exist."""


class MemoryCapacityError(MemoryError):
    """Raised when a memory store cannot accept more records."""


class MemorySerializationError(MemoryError):
    """Raised when memory serialization or deserialization fails."""
