# scios/cognitive_core/memory/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AbstractMemory(ABC):
    """
    Abstract base class for all memory types.
    Defines the common interface for storing, retrieving, and forgetting information.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def store(self, record: Dict[str, Any]) -> None:
        """Store a memory record."""
        pass

    @abstractmethod
    def retrieve(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve memory based on a query."""
        pass

    @abstractmethod
    def forget(self, record_id: str) -> None:
        """Forget or delete a memory record by ID."""
        pass

    @abstractmethod
    def all_records(self) -> list:
        """Return all stored records."""
        pass
