"""
SciOS Artifact Manager
======================

Responsibilities
----------------
- Manage artifacts produced by the Kernel.
- Track artifact metadata, type, status, lineage.
- Provide thread-safe registry of artifacts.
- Publish events via EventBus.

Does NOT:
- Handle file I/O or storage backends.
- Persist artifacts to disk/cloud.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
import threading

from .events import EventBus


__all__ = ["ArtifactType", "ArtifactStatus", "Artifact", "ArtifactManager"]


class ArtifactType(Enum):
    TEXT = auto()
    CODE = auto()
    IMAGE = auto()
    DATASET = auto()
    OTHER = auto()

    def __str__(self) -> str:
        return self.name.lower()


class ArtifactStatus(Enum):
    CREATED = "created"
    SAVED = "saved"
    ARCHIVED = "archived"
    DELETED = "deleted"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class Artifact:
    name: str
    type: ArtifactType
    content: Any
    status: ArtifactStatus = ArtifactStatus.CREATED
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"Artifact(name={self.name}, type={self.type}, "
            f"status={self.status.value}, content={self.content!r})"
        )


class ArtifactManager:
    """
    Thread-safe manager for artifacts.
    """

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self._artifacts: Dict[str, Artifact] = {}
        self._lock = threading.RLock()
        self.event_bus = event_bus or EventBus()

    # ==========================================================
    # Core API
    # ==========================================================

    def create(self, name: str, type: ArtifactType, content: Any) -> Artifact:
        """Create and register a new artifact."""
        with self._lock:
            artifact = Artifact(name=name, type=type, content=content)
            self._artifacts[name] = artifact
            self.event_bus.publish("artifact.created", artifact=artifact)
            return artifact

    def delete(self, name: str) -> None:
        """Delete an artifact by name."""
        with self._lock:
            if name in self._artifacts:
                artifact = self._artifacts.pop(name)
                artifact.status = ArtifactStatus.DELETED
                self.event_bus.publish("artifact.deleted", artifact=artifact)

    def get(self, name: str) -> Artifact:
        """Retrieve an artifact by name."""
        with self._lock:
            if name not in self._artifacts:
                raise KeyError(f"Artifact '{name}' not found.")
            return self._artifacts[name]

    def list(self) -> List[Artifact]:
        """Return all artifacts."""
        with self._lock:
            return list(self._artifacts.values())

    def clear(self) -> None:
        """Clear all artifacts."""
        with self._lock:
            self._artifacts.clear()
            self.event_bus.publish("artifact.cleared")

    # ==========================================================
    # Pythonic helpers
    # ==========================================================

    def __len__(self) -> int:
        return len(self._artifacts)

    def __iter__(self):
        with self._lock:
            return iter(tuple(self._artifacts.values()))

    def __contains__(self, artifact: object) -> bool:
        return isinstance(artifact, Artifact) and artifact.name in self._artifacts

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(artifacts={len(self)})"
