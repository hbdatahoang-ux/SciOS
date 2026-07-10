"""
SciOS MUSES Episodic Memory

Stores experiences, events and execution history.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4


class EpisodicMemory:
    """
    Episodic memory.

    Responsibilities
    ----------------
    - Store experiences
    - Retrieve experiences
    - Search history
    - Maintain chronological order
    """

    def __init__(self):
        self._episodes: List[Dict[str, Any]] = []

    def record(
        self,
        event: str,
        outcome: Any,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Record a new experience.
        """

        episode = {
            "id": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "outcome": outcome,
            "metadata": metadata or {},
        }

        self._episodes.append(episode)

        return episode

    def retrieve(self, episode_id: str):
        """
        Retrieve an episode by id.
        """

        for episode in self._episodes:
            if episode["id"] == episode_id:
                return episode

        return None

    def recent(self, limit: int = 10):
        """
        Return the most recent episodes.
        """

        return self._episodes[-limit:]

    def search(self, keyword: str):
        """
        Search episodes by event name.
        """

        keyword = keyword.lower()

        return [
            episode
            for episode in self._episodes
            if keyword in episode["event"].lower()
        ]

    def all(self):
        """
        Return all episodes.
        """

        return list(self._episodes)

    def clear(self):
        """
        Remove all episodes.
        """

        self._episodes.clear()

    def size(self) -> int:
        """
        Number of stored episodes.
        """

        return len(self._episodes)

    def status(self):
        """
        Runtime status.
        """

        return {
            "component": "EpisodicMemory",
            "episodes": self.size(),
        }
