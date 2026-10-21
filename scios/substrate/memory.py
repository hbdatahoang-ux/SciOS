"""
SciOS Memory Manager
====================

Low-level memory resource manager for the SciOS substrate.

Responsibilities
----------------
- Tensor allocation tracking
- Memory ownership
- Cache management
- Runtime memory statistics
- Future CPU/GPU unified allocator

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator
import threading
import uuid
import copy

if TYPE_CHECKING:
    from .tensor import SciOSTensor

__all__ = [
    "MemoryBlock",
    "MemoryManager",
]


# ==========================================================
# Memory Block
# ==========================================================

@dataclass(slots=True)
class MemoryBlock:
    """
    Represents one allocated tensor resource.
    """

    id: str

    tensor: SciOSTensor

    owner: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


# ==========================================================
# Memory Manager
# ==========================================================

class MemoryManager:
    """
    Runtime memory allocator.

    Tracks tensor allocations independently of the
    cognitive memory system.
    """

    def __init__(self) -> None:

        self._blocks: dict[str, MemoryBlock] = {}

        self._lock = threading.RLock()

    # ======================================================
    # Allocation
    # ======================================================

    def allocate(
        self,
        tensor: SciOSTensor,
        owner: str | None = None,
        **metadata: Any,
    ) -> str:
        """
        Register a tensor allocation.
        """

        block = MemoryBlock(
            id=str(uuid.uuid4()),
            tensor=tensor,
            owner=owner,
            metadata=dict(metadata),
        )

        with self._lock:
            self._blocks[block.id] = block

        return block.id

    def release(
        self,
        block_id: str,
    ) -> bool:
        """
        Release one allocation.

        Returns
        -------
        bool
            True if removed.
        """

        with self._lock:
            return self._blocks.pop(block_id, None) is not None

    def release_owner(
        self,
        owner: str,
    ) -> int:
        """
        Release every allocation owned by one owner.
        """

        with self._lock:

            ids = [
                block.id
                for block in self._blocks.values()
                if block.owner == owner
            ]

            for block_id in ids:
                self._blocks.pop(block_id, None)

            return len(ids)

    # ======================================================
    # Lookup
    # ======================================================

    def get(
        self,
        block_id: str,
    ) -> MemoryBlock | None:

        with self._lock:
            return self._blocks.get(block_id)

    def exists(
        self,
        block_id: str,
    ) -> bool:

        with self._lock:
            return block_id in self._blocks

    def items(self) -> list[MemoryBlock]:

        with self._lock:
            return list(self._blocks.values())

    def blocks(self) -> dict[str, MemoryBlock]:

        with self._lock:
            return dict(self._blocks)

    def owners(self) -> set[str]:

        with self._lock:

            return {
                block.owner
                for block in self._blocks.values()
                if block.owner is not None
            }

    # ======================================================
    # Maintenance
    # ======================================================

    def clear(self) -> None:

        with self._lock:
            self._blocks.clear()

    def snapshot(self) -> dict[str, MemoryBlock]:

        with self._lock:
            return copy.deepcopy(self._blocks)

    def restore(
        self,
        snapshot: dict[str, MemoryBlock],
    ) -> None:

        with self._lock:
            self._blocks = copy.deepcopy(snapshot)

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def allocations(self) -> int:

        with self._lock:
            return len(self._blocks)

    def stats(self) -> dict[str, Any]:
        """
        Memory usage statistics.
        """

        with self._lock:

            return {

                "allocations": len(self._blocks),

                "owners": len(
                    {
                        block.owner
                        for block in self._blocks.values()
                        if block.owner is not None
                    }
                ),

                "blocks": list(self._blocks),

            }

    def health(self) -> dict[str, Any]:

        return {

            "status": "healthy",

            "allocations": self.allocations,

            "owners": len(self.owners()),

        }

    def api_summary(self) -> dict[str, Any]:

        return {

            "class": self.__class__.__name__,

            "thread_safe": True,

            "snapshot_supported": True,

            "owner_tracking": True,

        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:

        return self.allocations

    def __contains__(
        self,
        block_id: str,
    ) -> bool:

        return self.exists(block_id)

    def __iter__(self) -> Iterator[MemoryBlock]:

        return iter(self.items())

    def __repr__(self) -> str:

        return (
            "MemoryManager("
            f"allocations={self.allocations}, "
            f"owners={len(self.owners())})"
        )