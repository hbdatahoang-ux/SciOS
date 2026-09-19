"""
SciOS Vector Storage
====================

Canonical vector storage abstraction and in-memory implementation.

Architecture
------------
VectorRecord
    ↓
VectorStorage
    ↓
VectorStore

Responsibilities
----------------
- Represent stored vector records.
- Define the backend storage contract.
- Provide an in-memory VectorStore implementation.
- Validate vector dimensions.
- Support CRUD operations.
- Support similarity search.
- Support metadata.
- Provide stable Python protocols.

Python 3.11+
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import sqrt
from typing import Any, Iterable, Iterator

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
    Canonical stored vector record.

    Parameters
    ----------
    id:
        Unique vector identifier.

    vector:
        Vector payload represented by SciOSTensor.

    metadata:
        Associated metadata.
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

    This class defines the low-level storage contract.

    Concrete implementations may include:

    - MemoryStorage
    - SQLiteStorage
    - LMDBStorage
    - QdrantStorage
    - CloudStorage

    VectorStore below is the canonical in-memory implementation.
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
        Insert or replace one vector record.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        record_id: str,
    ) -> VectorRecord | None:
        """
        Retrieve a vector record by ID.
        """
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        record: VectorRecord,
    ) -> None:
        """
        Update or replace an existing record.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        record_id: str,
    ) -> None:
        """
        Delete a record if it exists.
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
        Insert or replace multiple records.
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
        Return all stored IDs.
        """
        raise NotImplementedError

    @abstractmethod
    def values(
        self,
    ) -> list[VectorRecord]:
        """
        Return all stored records.
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
        Number of stored records.
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
        return self.get(record_id) is not None

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}("
            f"backend={self.backend!r}, "
            f"size={self.size})"
        )


# ==========================================================
# Public VectorStore
# ==========================================================


class VectorStore(VectorStorage):
    """
    Canonical in-memory vector store.

    This is the stable public API used by the current SciOS
    substrate layer.

    Features
    --------
    - Fixed vector dimension.
    - In-memory storage.
    - CRUD operations.
    - Duplicate IDs replace existing records.
    - Cosine similarity search.
    - Metadata support.
    - Iteration over VectorRecord objects.
    """

    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
        dimension: int,
    ) -> None:

        if isinstance(dimension, bool):
            raise TypeError(
                "dimension must be an integer"
            )

        if not isinstance(dimension, int):
            raise TypeError(
                "dimension must be an integer"
            )

        if dimension <= 0:
            raise ValueError(
                "dimension must be greater than zero"
            )

        self.dimension = dimension

        self._records: dict[str, VectorRecord] = {}

    # ======================================================
    # Backend
    # ======================================================

    @property
    def backend(
        self,
    ) -> str:
        """
        Return backend identifier.
        """
        return "memory"

    # ======================================================
    # Validation
    # ======================================================

    @staticmethod
    def _validate_id(
        record_id: str,
    ) -> None:

        if not isinstance(record_id, str):
            raise TypeError(
                "id must be a string"
            )

        if not record_id:
            raise ValueError(
                "id must not be empty"
            )

    def _normalize_vector(
        self,
        vector: Iterable[float] | SciOSTensor,
    ) -> SciOSTensor:
        """
        Convert input to SciOSTensor and validate dimension.
        """

        if isinstance(vector, SciOSTensor):
            tensor = vector
        else:
            tensor = SciOSTensor(vector)

        try:
            values = list(tensor)
        except TypeError as exc:
            raise TypeError(
                "vector must be iterable"
            ) from exc

        if len(values) != self.dimension:
            raise ValueError(
                "vector dimension must be "
                f"{self.dimension}, got {len(values)}"
            )

        return tensor

    @staticmethod
    def _vector_values(
        vector: SciOSTensor,
    ) -> list[float]:
        """
        Convert tensor values to plain floats.
        """

        return [
            float(value)
            for value in vector
        ]

    # ======================================================
    # CRUD
    # ======================================================

    def add(
        self,
        id: str,
        vector: Iterable[float] | SciOSTensor,
        metadata: Metadata | None = None,
    ) -> None:
        """
        Add a vector.

        Duplicate IDs replace the previous record.
        """

        self._validate_id(id)

        tensor = self._normalize_vector(vector)

        if metadata is None:
            metadata = Metadata()

        self._records[id] = VectorRecord(
            id=id,
            vector=tensor,
            metadata=metadata,
        )

    def get(
        self,
        record_id: str,
    ) -> list[float] | None:
        """
        Return a stored vector as a plain Python list.

        Returns None if the ID does not exist.
        """

        self._validate_id(record_id)

        record = self._records.get(record_id)

        if record is None:
            return None

        return self._vector_values(record.vector)

    def get_record(
        self,
        record_id: str,
    ) -> VectorRecord | None:
        """
        Return the complete VectorRecord.

        This is the record-level API while get() remains
        compatible with the public vector API.
        """

        self._validate_id(record_id)

        return self._records.get(record_id)

    def update(
        self,
        record: VectorRecord,
    ) -> None:
        """
        Insert or replace a VectorRecord.
        """

        if not isinstance(record, VectorRecord):
            raise TypeError(
                "record must be a VectorRecord"
            )

        self._validate_id(record.id)

        self._normalize_vector(record.vector)

        self._records[record.id] = record

    def delete(
        self,
        record_id: str,
    ) -> None:
        """
        Delete a vector if present.
        """

        self._validate_id(record_id)

        self._records.pop(
            record_id,
            None,
        )

    def remove(
        self,
        record_id: str,
    ) -> None:
        """
        Compatibility alias for delete().
        """

        self.delete(record_id)

    # ======================================================
    # Batch
    # ======================================================

    def add_many(
        self,
        records: Iterable[VectorRecord],
    ) -> None:
        """
        Add multiple VectorRecord objects.
        """

        for record in records:
            self.update(record)

    # ======================================================
    # Query
    # ======================================================

    def ids(
        self,
    ) -> list[str]:
        """
        Return stored IDs in insertion order.
        """

        return list(
            self._records.keys()
        )

    def values(
        self,
    ) -> list[VectorRecord]:
        """
        Return all stored records.
        """

        return list(
            self._records.values()
        )

    def exists(
        self,
        record_id: str,
    ) -> bool:
        """
        Check whether a vector exists.
        """

        self._validate_id(record_id)

        return record_id in self._records

    def empty(
        self,
    ) -> bool:
        """
        Return True when the store contains no vectors.
        """

        return self.size == 0

    # ======================================================
    # Similarity
    # ======================================================

    @staticmethod
    def _cosine_similarity(
        left: list[float],
        right: list[float],
    ) -> float:
        """
        Calculate cosine similarity.

        Zero vectors return similarity 0.0.
        """

        dot = sum(
            a * b
            for a, b in zip(left, right)
        )

        left_norm = sqrt(
            sum(
                value * value
                for value in left
            )
        )

        right_norm = sqrt(
            sum(
                value * value
                for value in right
            )
        )

        if left_norm == 0.0:
            return 0.0

        if right_norm == 0.0:
            return 0.0

        return dot / (
            left_norm * right_norm
        )

    def search(
        self,
        vector: Iterable[float] | SciOSTensor,
        top_k: int = 10,
    ) -> list[VectorRecord]:
        """
        Search by cosine similarity.

        Results are ordered from highest similarity
        to lowest similarity.

        Parameters
        ----------
        vector:
            Query vector.

        top_k:
            Maximum number of results.

        Returns
        -------
        list[VectorRecord]
            Matching records ordered by similarity.
        """

        if isinstance(top_k, bool):
            raise TypeError(
                "top_k must be an integer"
            )

        if not isinstance(top_k, int):
            raise TypeError(
                "top_k must be an integer"
            )

        if top_k <= 0:
            return []

        query = self._normalize_vector(vector)

        query_values = self._vector_values(
            query
        )

        scored: list[
            tuple[float, int, VectorRecord]
        ] = []

        for index, record in enumerate(
            self._records.values()
        ):

            record_values = self._vector_values(
                record.vector
            )

            similarity = self._cosine_similarity(
                query_values,
                record_values,
            )

            # Keep insertion order as deterministic
            # tie-breaker.
            scored.append(
                (
                    similarity,
                    index,
                    record,
                )
            )

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        return [
            record
            for _, _, record
            in scored[:top_k]
        ]

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def size(
        self,
    ) -> int:
        """
        Number of stored vectors.
        """

        return len(
            self._records
        )

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Return stable store status.
        """

        return {
            "backend": self.backend,
            "dimension": self.dimension,
            "size": self.size,
        }

    # ======================================================
    # Mutation
    # ======================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all vectors.
        """

        self._records.clear()

    # ======================================================
    # Python Protocol
    # ======================================================

    def __iter__(
        self,
    ) -> Iterator[VectorRecord]:
        """
        Iterate over stored records.
        """

        return iter(
            self._records.values()
        )