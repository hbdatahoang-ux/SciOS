"""
SciOS MUSES Memory Archive

Persistence layer for memory subsystems.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class MemoryArchive:
    """
    Memory persistence layer.

    Responsibilities
    ----------------
    - Save memory state
    - Load memory state
    - Export snapshots
    - Import snapshots
    """

    def __init__(self, root: str = "data/memory"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        name: str,
        data: Dict[str, Any],
    ) -> Path:
        """
        Save memory snapshot.
        """

        path = self.root / f"{name}.json"

        with path.open("w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )

        return path

    def load(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """
        Load memory snapshot.
        """

        path = self.root / f"{name}.json"

        if not path.exists():
            return {}

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def exists(self, name: str) -> bool:
        """
        Check whether a snapshot exists.
        """

        return (self.root / f"{name}.json").exists()

    def delete(self, name: str) -> bool:
        """
        Delete a snapshot.
        """

        path = self.root / f"{name}.json"

        if path.exists():
            path.unlink()
            return True

        return False

    def list(self):
        """
        List available snapshots.
        """

        return sorted(
            file.stem
            for file in self.root.glob("*.json")
        )

    def clear(self):
        """
        Remove every snapshot.
        """

        for file in self.root.glob("*.json"):
            file.unlink()

    def status(self):
        """
        Runtime status.
        """

        return {
            "component": "MemoryArchive",
            "root": str(self.root),
            "snapshots": len(self.list()),
        }