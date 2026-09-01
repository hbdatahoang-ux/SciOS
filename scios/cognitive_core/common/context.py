from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass
class CognitiveContext:
    """
    Shared state container for Cognitive Core execution.

    CognitiveContext carries mutable execution state between cognitive
    stages while keeping execution metadata separate from stage data.

    Attributes:
        context_id:
            Unique identifier for this execution context.
        data:
            Mutable key-value state shared between cognitive stages.
        metadata:
            Mutable metadata associated with the execution.
        stage:
            Name of the currently active cognitive stage, if any.
    """

    context_id: UUID = field(default_factory=uuid4)
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    stage: str | None = None

    # ==========================================================
    # Core API
    # ==========================================================

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the context data.

        Args:
            key: Data key.
            value: Value associated with the key.
        """
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from context data.

        Args:
            key: Data key.
            default: Value returned when the key does not exist.

        Returns:
            Stored value or ``default`` when absent.
        """
        return self.data.get(key, default)

    def update_metadata(self, key: str, value: Any) -> None:
        """
        Store a value in context metadata.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a metadata value.

        Args:
            key: Metadata key.
            default: Value returned when the key does not exist.

        Returns:
            Stored metadata value or ``default`` when absent.
        """
        return self.metadata.get(key, default)

    # ==========================================================
    # Utility
    # ==========================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a detached snapshot of the current context state.

        The returned ``data`` and ``metadata`` mappings are shallow copies,
        so modifying them does not modify the corresponding context mappings.

        Returns:
            Dictionary containing the context identifier, current stage,
            data, and metadata.
        """
        return {
            "id": str(self.context_id),
            "stage": self.stage,
            "data": dict(self.data),
            "metadata": dict(self.metadata),
        }

    def clear(self) -> None:
        """
        Clear execution state while preserving the context identity.

        ``context_id`` is intentionally preserved so the same execution
        context can be reused without losing its identity.
        """
        self.data.clear()
        self.metadata.clear()
        self.stage = None