"""
SciOS Collaboration Protocol

Defines communication rules for cognitive agents.
"""

from typing import Dict, List

from .message import Message


class Protocol:
    """
    Collaboration protocol.

    Responsibilities
    ----------------
    - Validate messages
    - Define supported message types
    - Verify sender/receiver
    """

    SUPPORTED_TYPES = {
        "request",
        "response",
        "event",
        "broadcast",
    }

    def validate(self, message: Message) -> bool:
        """
        Validate a collaboration message.
        """

        if not message.sender:
            return False

        if not message.receiver:
            return False

        if message.message_type not in self.SUPPORTED_TYPES:
            return False

        return True

    def supported_types(self) -> List[str]:
        """
        Return supported message types.
        """
        return sorted(self.SUPPORTED_TYPES)

    def describe(self) -> Dict:
        """
        Protocol metadata.
        """
        return {
            "name": "SciOS Collaboration Protocol",
            "version": "0.1.3",
            "supported_types": self.supported_types(),
        }

    def status(self):
        """
        Protocol status.
        """
        return {
            "component": "Protocol",
            "status": "ready",
        }
