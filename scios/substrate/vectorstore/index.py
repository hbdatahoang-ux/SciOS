"""
SciOS Vector Index
==================

Backend-independent vector indexing abstraction.

Responsibilities
----------------
- Vector indexing
- Fast lookup
- Nearest-neighbor candidate retrieval
- Backend abstraction
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from scios.substrate.tensor import SciOSTensor

__all__ = [
    "IndexType",
    "SearchResult",
    "VectorIndex",
]


# ==========================================================
# Index Types
# ==========================================================

class IndexType(str, Enum):
    """
    Supported index implementations.
    """

    FLAT = "flat"

    HNSW = "hnsw"

    IVF = "ivf"

    ANNOY = "annoy"

    CUSTOM = "custom"


# ==========================================================
# Search Result
# ==========================================================

@dataclass(slots=True)
class SearchResult:
    """
    Result returned by an index lookup.
    """

    id: str

    score: float


# ==========================================================
# Abstract Vector Index
# ==========================================================

class VectorIndex(ABC):
    """
    Abstract vector index.

    An index accelerates nearest-neighbor retrieval.

    The index does NOT own vectors.
    Vectors remain inside VectorStorage.
    """

    # ======================================================
    # Information
    # ======================================================

    @property
    @abstractmethod
    def index_type(self) -> IndexType:
        """
        Index implementation.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def size(self) -> int:
        """
        Number of indexed vectors.
        """
        raise NotImplementedError

    # ======================================================
    # Index Management
    # ======================================================

    @abstractmethod
    def add(
        self,
        record_id: str,
        vector: SciOSTensor,
    ) -> None:
        """
        Add one vector reference.
        """
        raise NotImplementedError

    @abstractmethod
    def add_many(
        self,
        items: Iterable[tuple[str, SciOSTensor]],
    ) -> None:
        """
        Add multiple vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        record_id: str,
    ) -> None:
        """
        Remove a vector from the index.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """
        Remove every indexed vector.
        """
        raise NotImplementedError

    # ======================================================
    # Search
    # ======================================================

    @abstractmethod
    def search(
        self,
        query: SciOSTensor,
        k: int = 10,
    ) -> list[SearchResult]:
        """
        Return nearest-neighbor candidates.
        """
        raise NotImplementedError

    # ======================================================
    # Persistence
    # ======================================================

    @abstractmethod
    def build(self) -> None:
        """
        Build or rebuild the index.
        """
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        path: str,
    ) -> None:
        """
        Persist index.
        """
        raise NotImplementedError

    @abstractmethod
    def load(
        self,
        path: str,
    ) -> None:
        """
        Restore index.
        """
        raise NotImplementedError

    # ======================================================
    # Python
    # ======================================================

    def __len__(self) -> int:

        return self.size

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"type={self.index_type.value}, "
            f"size={self.size})"
        )