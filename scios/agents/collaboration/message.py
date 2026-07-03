"""
SciOS Collaboration Message

Standard message exchanged between cognitive agents.
"""

from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import uuid4
from datetime import datetime


@dataclass(slots=True)
class Message:
    """
    Standard collaboration message.

    Responsibilities
    ----------------
    - Represent inter-agent communication
    - Carry payload and metadata
    """

    sender: str
    receiver: str
    payload: Any

    message_type: str = "request"

    message_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize message.
        """

        return {
            "id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.message_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Deserialize message.
        """

        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            payload=data["payload"],
            message_type=data.get("type", "request"),
            message_id=data.get(
                "id",
                str(uuid4()),
            ),
            timestamp=data.get(
                "timestamp",
                datetime.utcnow().isoformat(),
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    def __repr__(self):

        return (
            f"Message("
            f"{self.sender} -> {self.receiver}, "
            f"type={self.message_type})"
        )