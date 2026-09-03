from __future__ import annotations

from abc import ABC, abstractmethod

from .record import MemoryRecord
from .types import MemoryId


class MemoryStore(ABC):
    """Abstract contract for a memory store."""

    def __init__(self, *, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")

        self.name = name

    @abstractmethod
    def store(self, record: MemoryRecord) -> MemoryRecord:
        """Store a memory record and return the stored record."""
        raise NotImplementedError

    @abstractmethod
    def get(self, record_id: MemoryId) -> MemoryRecord | None:
        """Return a record by ID, or None when it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, record_id: MemoryId) -> bool:
        """Delete a record and return whether it existed."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all records from the store."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored records."""
        raise NotImplementedError

    @abstractmethod
    def all(self) -> tuple[MemoryRecord, ...]:
        """Return all records as an immutable tuple."""
        raise NotImplementedError
