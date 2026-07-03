"""
SciOS Collaboration Session

Represents a collaborative execution session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from .message import Message


@dataclass(slots=True)
class Session:
    """
    Collaboration session.

    Responsibilities
    ----------------
    - Track participating agents
    - Store exchanged messages
    - Maintain session state
    """

    session_id: str = field(default_factory=lambda: str(uuid4()))

    name: str = "default"

    participants: List[str] = field(default_factory=list)

    messages: List[Message] = field(default_factory=list)

    state: Dict = field(default_factory=dict)

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    active: bool = True

    def add_participant(self, agent: str):
        """Register an agent in the session."""
        if agent not in self.participants:
            self.participants.append(agent)

    def remove_participant(self, agent: str):
        """Remove an agent from the session."""
        if agent in self.participants:
            self.participants.remove(agent)

    def add_message(self, message: Message):
        """Append a message to the session."""
        self.messages.append(message)

    def update_state(self, key: str, value):
        """Update shared session state."""
        self.state[key] = value

    def get_state(self, key: str, default=None):
        """Read session state."""
        return self.state.get(key, default)

    def close(self):
        """Close the session."""
        self.active = False

    def summary(self):
        """Return session summary."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "participants": self.participants,
            "messages": len(self.messages),
            "active": self.active,
        }

    def status(self):
        """Return runtime status."""
        return {
            "component": "Session",
            "session": self.session_id,
            "active": self.active,
            "participants": len(self.participants),
            "messages": len(self.messages),
        }

    def __repr__(self):
        return (
            f"Session("
            f"id={self.session_id}, "
            f"participants={len(self.participants)}, "
            f"messages={len(self.messages)})"
        )