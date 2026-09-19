# ==============================================================================
# SciOS Runtime Science
# Provenance Lineage
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .models import ProvenanceRecord


# ==============================================================================
# Exceptions
# ==============================================================================


class LineageError(RuntimeError):
    """Base exception for provenance lineage failures."""


class DuplicateRecordError(LineageError, ValueError):
    """Raised when a record ID already exists in the lineage."""


class MissingParentError(LineageError, ValueError):
    """Raised when a record references a missing parent."""


class LineageCycleError(LineageError, ValueError):
    """Raised when adding a record would create a lineage cycle."""


class RecordNotFoundError(LineageError, KeyError):
    """Raised when a requested provenance record does not exist."""


# ==============================================================================
# Lineage
# ==============================================================================


@dataclass(frozen=True, slots=True)
class ProvenanceLineage:
    """
    Immutable container for a scientific provenance graph.

    The lineage is represented as a directed graph:

        parent -> child

    Each ``ProvenanceRecord`` stores its parent IDs. The lineage validates
    those references and prevents cyclic provenance.
    """

    _records: dict[str, ProvenanceRecord]

    def __init__(
        self,
        records: tuple[ProvenanceRecord, ...] = (),
    ) -> None:
        record_map: dict[str, ProvenanceRecord] = {}

        for record in records:
            if record.id in record_map:
                raise DuplicateRecordError(
                    f"Duplicate provenance record: {record.id}"
                )

            record_map[record.id] = record

        lineage = object.__new__(type(self))
        object.__setattr__(lineage, "_records", record_map)

        lineage.validate()

        object.__setattr__(self, "_records", record_map)

    # --------------------------------------------------------------------------
    # Basic access
    # --------------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of records in the lineage."""
        return len(self._records)

    def __iter__(self) -> Iterator[ProvenanceRecord]:
        """Iterate over records in insertion order."""
        return iter(self._records.values())

    def contains(self, record_id: str) -> bool:
        """Return whether ``record_id`` exists."""
        return record_id in self._records

    def get(self, record_id: str) -> ProvenanceRecord:
        """
        Return a record by ID.

        Raises
        ------
        RecordNotFoundError
            If the record does not exist.
        """
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise RecordNotFoundError(record_id) from exc

    # --------------------------------------------------------------------------
    # Graph relationships
    # --------------------------------------------------------------------------

    def parents(self, record_id: str) -> tuple[ProvenanceRecord, ...]:
        """Return the direct parents of ``record_id``."""
        record = self.get(record_id)

        return tuple(
            self.get(parent_id)
            for parent_id in record.parent_ids
        )

    def children(self, record_id: str) -> tuple[ProvenanceRecord, ...]:
        """Return the direct children of ``record_id``."""
        self.get(record_id)

        return tuple(
            record
            for record in self._records.values()
            if record_id in record.parent_ids
        )

    def ancestors(self, record_id: str) -> tuple[ProvenanceRecord, ...]:
        """
        Return all ancestors of ``record_id``.

        Results are returned in deterministic breadth-first order.
        """
        self.get(record_id)

        result: list[ProvenanceRecord] = []
        visited: set[str] = set()
        queue = list(self.get(record_id).parent_ids)

        while queue:
            current_id = queue.pop(0)

            if current_id in visited:
                continue

            visited.add(current_id)

            current = self.get(current_id)
            result.append(current)

            queue.extend(current.parent_ids)

        return tuple(result)

    # --------------------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the complete provenance graph.

        Invariants
        ----------
        1. Every parent reference must resolve to an existing record.
        2. No record may reference itself.
        3. No directed cycle may exist.
        """
        self._validate_parent_references()
        self._validate_cycles()

    def _validate_parent_references(self) -> None:
        for record in self._records.values():
            for parent_id in record.parent_ids:
                if parent_id not in self._records:
                    raise MissingParentError(
                        f"Record {record.id!r} references missing "
                        f"parent {parent_id!r}"
                    )

    def _validate_cycles(self) -> None:
        for record_id in self._records:
            self._validate_no_cycle_from(record_id)

    def _validate_no_cycle_from(self, start_id: str) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(record_id: str) -> None:
            if record_id in visiting:
                raise LineageCycleError(
                    f"Cycle detected involving record {record_id!r}"
                )

            if record_id in visited:
                return

            visiting.add(record_id)

            record = self.get(record_id)

            for parent_id in record.parent_ids:
                visit(parent_id)

            visiting.remove(record_id)
            visited.add(record_id)

        visit(start_id)