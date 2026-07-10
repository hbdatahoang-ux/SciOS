"""
SciOS Collaboration Agent

Base interface for collaborative cognitive agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .message import Message


class CollaborativeAgent(ABC):
    """
    Base class for collaborative agents.

    Responsibilities
    ----------------
    - Receive messages
    - Process requests
    - Send responses
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def receive(self, message: Message) -> Any:
        """
        Receive a collaboration message.
        """
        raise NotImplementedError

    @abstractmethod
    def process(self, payload: Any) -> Any:
        """
        Execute cognitive processing.
        """
        raise NotImplementedError

    def status(self) -> dict:
        """
        Agent status.
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "status": "ready",
        }

    def __repr__(self):

        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}')"
        )
