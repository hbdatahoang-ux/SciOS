"""
SciOS Vector Storage
====================

Abstract storage layer for the SciOS VectorStore.

Responsibilities
----------------
- Persistent vector storage
- CRUD operations
- Metadata persistence
- Backend abstraction
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable


from scios.substrate.tensor import SciOSTensor
from .metadata import Metadata


__all__ = [
    "VectorRecord",
    "VectorStorage",
    "VectorStore",
]


# ==========================================================
# Vector Record
# ==========================================================


@dataclass(slots=True)
class VectorRecord:
    """
    A stored vector record.
    """

    id: str

    vector: SciOSTensor

    metadata: Metadata



# ==========================================================
# Abstract Storage
# ==========================================================


class VectorStorage(ABC):
    """
    Abstract vector storage backend.

    Low-level storage contract.

    Implementations:
    - MemoryStorage
    - SQLiteStorage
    - LMDBStorage
    - QdrantStorage
    - CloudStorage
    """


    # ======================================================
    # CRUD
    # ======================================================


    @abstractmethod
    def add(
        self,
        record: VectorRecord,
    ) -> None:
        """
        Insert one vector record.
        """
        raise NotImplementedError



    @abstractmethod
    def get(
        self,
        record_id: str,
    ) -> VectorRecord | None:
        """
        Retrieve vector record.
        """
        raise NotImplementedError



    @abstractmethod
    def update(
        self,
        record: VectorRecord,
    ) -> None:
        """
        Update existing record.
        """
        raise NotImplementedError



    @abstractmethod
    def delete(
        self,
        record_id: str,
    ) -> None:
        """
        Delete record.
        """
        raise NotImplementedError



    # ======================================================
    # Batch
    # ======================================================


    @abstractmethod
    def add_many(
        self,
        records: Iterable[VectorRecord],
    ) -> None:
        """
        Insert multiple records.
        """
        raise NotImplementedError



    # ======================================================
    # Query
    # ======================================================


    @abstractmethod
    def ids(
        self,
    ) -> list[str]:
        """
        Return stored IDs.
        """
        raise NotImplementedError



    @abstractmethod
    def values(
        self,
    ) -> list[VectorRecord]:
        """
        Return all records.
        """
        raise NotImplementedError



    @abstractmethod
    def clear(
        self,
    ) -> None:
        """
        Remove all records.
        """
        raise NotImplementedError



    # ======================================================
    # Statistics
    # ======================================================


    @property
    @abstractmethod
    def size(
        self,
    ) -> int:
        """
        Number of stored vectors.
        """
        raise NotImplementedError



    @property
    @abstractmethod
    def backend(
        self,
    ) -> str:
        """
        Backend identifier.
        """
        raise NotImplementedError



    # ======================================================
    # Python Protocol
    # ======================================================


    def __len__(
        self,
    ) -> int:

        return self.size



    def __contains__(
        self,
        record_id: str,
    ) -> bool:

        return (
            self.get(record_id)
            is not None
        )



    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"backend='{self.backend}', "
            f"size={self.size})"
        )



# ==========================================================
# Public VectorStore API
# ==========================================================


class VectorStore(VectorStorage):
    """
    Public VectorStore interface.

    Compatibility layer for SciOS modules.

    VectorStore represents the user-facing
    vector database abstraction.

    It extends VectorStorage so existing
    backend implementations remain compatible.
    """

    pass