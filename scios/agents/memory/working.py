"""
SciOS MUSES Working Memory

Temporary memory used during reasoning and execution.
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

    def __init__(self):
        self._state: Dict[str, Any] = {}

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value in working memory.
        """
        self._state[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a value.
        """
        return self._state.get(key, default)

    def update(
        self,
        values: Dict[str, Any],
    ) -> None:
        """
        Update multiple values.
        """
        self._state.update(values)

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a key.
        """
        self._state.pop(key, None)

    def clear(self) -> None:
        """
        Clear working memory.
        """
        self._state.clear()

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a copy of the current state.
        """
        return dict(self._state)

    def size(self) -> int:
        """
        Number of active variables.
        """
        return len(self._state)

    def status(self):
        """
        Runtime status.
        """
        return {
            "component": "WorkingMemory",
            "variables": self.size(),
        }

    def __contains__(self, key):
        return key in self._state

    def __repr__(self):
        return (
            f"WorkingMemory("
            f"variables={self.size()})"
        )