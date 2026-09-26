"""
SciOS Kernel Artifact Manager
=============================

Artifact management subsystem for the SciOS Kernel.

Responsibilities
----------------
- Store execution artifacts.
- Retrieve artifacts.
- Remove artifacts.
- Tag and query artifacts.
- Maintain artifact metadata.

Design Goals
------------
- Thread-safe
- Runtime independent
- Immutable-friendly
- Extensible
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Any
import uuid


class ArtifactManager:
    """
    Central artifact repository.
    """

    def __init__(self) -> None:

        self._artifacts: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    # ==========================================================
    # Creation
    # ==========================================================

    def create(
        self,
        data: Any,
        *,
        name: str | None = None,
        kind: str = "generic",
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """
        Create and store an artifact.

        Returns
        -------
        str
            Artifact identifier.
        """

        artifact_id = uuid.uuid4().hex

        artifact = {
            "id": artifact_id,
            "name": name or artifact_id,
            "kind": kind,
            "data": data,
            "metadata": metadata or {},
            "tags": list(tags or []),
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        with self._lock:
            self._artifacts[artifact_id] = artifact

        return artifact_id

    # ==========================================================
    # Retrieval
    # ==========================================================

    def get(
        self,
        artifact_id: str,
    ) -> dict[str, Any]:
        """
        Retrieve an artifact.
        """

        with self._lock:

            if artifact_id not in self._artifacts:
                raise KeyError(
                    f"Unknown artifact '{artifact_id}'."
                )

            return self._artifacts[artifact_id]

    def find_by_name(
        self,
        name: str,
    ) -> dict[str, Any] | None:

        with self._lock:

            for artifact in self._artifacts.values():

                if artifact["name"] == name:
                    return artifact

        return None

    def find_by_tag(
        self,
        tag: str,
    ) -> list[dict[str, Any]]:

        with self._lock:

            return [
                artifact
                for artifact in self._artifacts.values()
                if tag in artifact["tags"]
            ]

    def find_by_kind(
        self,
        kind: str,
    ) -> list[dict[str, Any]]:

        with self._lock:

            return [
                artifact
                for artifact in self._artifacts.values()
                if artifact["kind"] == kind
            ]

    # ==========================================================
    # Update
    # ==========================================================

    def update_metadata(
        self,
        artifact_id: str,
        **metadata: Any,
    ) -> None:

        artifact = self.get(artifact_id)

        artifact["metadata"].update(metadata)

    def add_tag(
        self,
        artifact_id: str,
        tag: str,
    ) -> None:

        artifact = self.get(artifact_id)

        if tag not in artifact["tags"]:
            artifact["tags"].append(tag)

    def remove_tag(
        self,
        artifact_id: str,
        tag: str,
    ) -> None:

        artifact = self.get(artifact_id)

        if tag in artifact["tags"]:
            artifact["tags"].remove(tag)

    # ==========================================================
    # Removal
    # ==========================================================

    def delete(
        self,
        artifact_id: str,
    ) -> None:

        with self._lock:

            if artifact_id not in self._artifacts:
                raise KeyError(
                    f"Unknown artifact '{artifact_id}'."
                )

            del self._artifacts[artifact_id]

    def clear(self) -> None:

        with self._lock:
            self._artifacts.clear()

    # ==========================================================
    # Query
    # ==========================================================

    def ids(self) -> list[str]:

        with self._lock:
            return sorted(self._artifacts.keys())

    def values(self) -> list[dict[str, Any]]:

        with self._lock:
            return list(self._artifacts.values())

    def count(self) -> int:

        with self._lock:
            return len(self._artifacts)

    # ==========================================================
    # Export
    # ==========================================================

    def status(self) -> dict[str, Any]:

        return {
            "artifacts": self.count(),
            "ids": self.ids(),
        }

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __contains__(
        self,
        artifact_id: object,
    ) -> bool:

        return (
            isinstance(artifact_id, str)
            and artifact_id in self._artifacts
        )

    def __getitem__(
        self,
        artifact_id: str,
    ) -> dict[str, Any]:

        return self.get(artifact_id)

    def __len__(self) -> int:

        return self.count()

    def __iter__(self):

        return iter(self.values())

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"artifacts={self.count()})"
        )