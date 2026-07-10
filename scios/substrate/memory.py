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
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import threading
import uuid

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

        block_id = str(uuid.uuid4())

        block = MemoryBlock(
            id=block_id,
            tensor=tensor,
            owner=owner,
            metadata=metadata,
        )

        with self._lock:
            self._blocks[block_id] = block

        return block_id

    def release(
        self,
        block_id: str,
    ) -> None:
        """
        Release an allocated block.
        """

        with self._lock:
            self._blocks.pop(block_id, None)

    # ======================================================
    # Lookup
    # ======================================================

    def get(
        self,
        block_id: str,
    ) -> MemoryBlock | None:

        return self._blocks.get(block_id)

    def exists(
        self,
        block_id: str,
    ) -> bool:

        return block_id in self._blocks

    # ======================================================
    # Maintenance
    # ======================================================

    def clear(self) -> None:

        with self._lock:
            self._blocks.clear()

    # ======================================================
    # Statistics
    # ======================================================

    @property
    def allocations(self) -> int:

        return len(self._blocks)

    def stats(self) -> dict[str, Any]:
        """
        Memory usage statistics.
        """

        return {

            "allocations": len(self._blocks),

            "owners": len(
                {
                    b.owner
                    for b in self._blocks.values()
                    if b.owner is not None
                }
            ),
        }

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:

        return len(self._blocks)

    def __contains__(
        self,
        block_id: str,
    ) -> bool:

        return block_id in self._blocks

    def __repr__(self) -> str:

        return (
            "MemoryManager("
            f"allocations={len(self._blocks)})"
        )
