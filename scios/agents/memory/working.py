"""
SciOS MUSES Working Memory
==========================

Temporary memory used during reasoning and execution.
Also supports stable key-value contract for unit tests.
"""

from __future__ import annotations
from typing import Any, Dict


class WorkingMemory:
    """
    Working memory.

    Responsibilities
    ----------------
    - Maintain active execution context
    - Store temporary variables
    - Share state between cognitive modules
    """

    def __init__(self, capacity: int | None = None):
        self._state: Dict[str, Any] = {}
        self.capacity = capacity

    # -------------------------------------------------
    # Original API (for reasoning context)
    # -------------------------------------------------
    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def update(self, values: Dict[str, Any]) -> None:
        self._state.update(values)

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._state)

    def size(self) -> int:
        return len(self._state)

    # -------------------------------------------------
    # Stable contract API (for tests)
    # -------------------------------------------------
    def store(self, key: str, value: Any) -> None:
        if self.capacity is not None and key not in self._state and len(self._state) >= self.capacity:
            raise Exception("Memory capacity exceeded")
        self._state[key] = value

    def retrieve(self, key: str) -> Any:
        if key not in self._state:
            raise KeyError(f"Key '{key}' not found in memory")
        return self._state[key]

    def exists(self, key: str) -> bool:
        return key in self._state

    def remove(self, key: str) -> None:
        if key in self._state:
            del self._state[key]

    def clear(self) -> None:
        self._state.clear()

    def empty(self) -> bool:
        return len(self._state) == 0

    def status(self) -> dict:
        return {
            "entries": len(self._state),
            "capacity": self.capacity,
        }

    # -------------------------------------------------
    # Dict-like behavior
    # -------------------------------------------------
    def keys(self):
        return self._state.keys()

    def values(self):
        return self._state.values()

    def items(self):
        return self._state.items()

    def __len__(self) -> int:
        return len(self._state)

    def __iter__(self):
        return iter(self._state.items())

    def __contains__(self, key: str) -> bool:
        return key in self._state

    def __repr__(self) -> str:
        return f"WorkingMemory(entries={len(self)}, capacity={self.capacity})"
