"""
SciOS Collaboration

Multi-agent collaboration subsystem.

Responsibilities
----------------
- Agent coordination
- Message passing
- Collaboration protocols
- Shared task execution
"""

from .coordinator import Coordinator
from .message import Message
from .protocol import Protocol

__all__ = [
    "Coordinator",
    "Message",
    "Protocol",
]
