"""
SciOS Semantic Memory
=====================

Concrete semantic memory implementation.

Responsibilities
----------------
- Store semantic facts
- Retrieve semantic knowledge
- Forget knowledge
- Enumerate records
- Expose backward-compatible fact API
"""

from __future__ import annotations

from typing import Any

from .base import AbstractMemory
from .record import MemoryRecord


class SemanticMemory(AbstractMemory):
    """
    Stores semantic knowledge (facts, concepts, relationships).

    This implementation is intentionally lightweight while exposing
    a stable API for both the modern memory subsystem and legacy
    reasoning components.
    """

    def __init__(
        self,
        name: str = "SemanticMemory",
    ) -> None:

        super().__init__(name)

        self._records: list[MemoryRecord] = []

    # ======================================================
    # Store
    # ======================================================

    def store(
        self,
        record: dict[str, Any],
    ) -> None:
        """
        Store a semantic memory record.
        """

        self._records.append(
            MemoryRecord(**record)
        )

    # ======================================================
    # Retrieve
    # ======================================================

    def retrieve(
        self,
        query: dict[str, Any],
    ) -> MemoryRecord | None:
        """
        Retrieve the first matching semantic record.

        Supported query keys
        --------------------
        - keyword
        - id
        - content
        """

        keyword = query.get("keyword")
        record_id = query.get("id")
        content = query.get("content")

        for record in self._records:

            if (
                record_id is not None
                and getattr(record, "id", None) == record_id
            ):
                return record

            text = str(
                getattr(record, "content", "")
            )

            if (
                keyword is not None
                and keyword.lower() in text.lower()
            ):
                return record

            if (
                content is not None
                and content.lower() in text.lower()
            ):
                return record

        return None

    # ======================================================
    # Forget
    # ======================================================

    def forget(
        self,
        record_id: str,
    ) -> None:
        """
        Remove a semantic record by ID.
        """

        self._records = [
            record
            for record in self._records
            if getattr(record, "id", None) != record_id
        ]

    # ======================================================
    # Utilities
    # ======================================================

    def clear(self) -> None:
        """
        Remove every semantic record.
        """

        self._records.clear()

    def all_records(self) -> list[MemoryRecord]:
        """
        Return all semantic records.
        """

        return list(self._records)

    def size(self) -> int:
        """
        Number of semantic records.
        """

        return len(self._records)

    def is_empty(self) -> bool:
        """
        Whether the memory is empty.
        """

        return len(self._records) == 0

    # ======================================================
    # Compatibility API
    # ======================================================

    def all_facts(self) -> dict[str, Any]:
        """
        Return semantic facts.

        Backward-compatible API required by older reasoning
        modules. Facts are keyed by record ID when available,
        otherwise by record content.
        """

        facts: dict[str, Any] = {}

        for record in self._records:

            key = (
                getattr(record, "id", None)
                or getattr(record, "content", "")
            )

            value = getattr(
                record,
                "content",
                None,
            )

            facts[str(key)] = value

        return facts

    def contains(
        self,
        keyword: str,
    ) -> bool:
        """
        Check whether a keyword exists.
        """

        return self.retrieve(
            {"keyword": keyword}
        ) is not None

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self):
        return iter(self._records)

    def __contains__(
        self,
        keyword: str,
    ) -> bool:
        return self.contains(keyword)

    def __bool__(self) -> bool:
        return bool(self._records)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(records={len(self._records)})"
        )