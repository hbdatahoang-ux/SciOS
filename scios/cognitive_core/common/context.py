from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass
class CognitiveContext:
    """
    CognitiveContext = Shared state container for pipeline execution.
    """

    context_id: UUID = field(default_factory=uuid4)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    stage: str | None = None

    # ==========================================================
    # Core API
    # ==========================================================

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in context data.
        """
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from context data.
        """
        return self.data.get(key, default)

    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update metadata entry.
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Retrieve metadata entry.
        """
        return self.metadata.get(key, default)

    # ==========================================================
    # Utility
    # ==========================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a snapshot of current context state.
        """
        return {
            "id": str(self.context_id),
            "stage": self.stage,
            "data": dict(self.data),
            "metadata": dict(self.metadata),
        }

    def clear(self) -> None:
        """
        Clear context data and metadata.
        """
        self.data.clear()
        self.metadata.clear()
        self.stage = None
