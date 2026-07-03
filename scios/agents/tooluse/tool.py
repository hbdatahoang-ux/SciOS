"""
SciOS Tool

Base interface for executable tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Tool(ABC):
    """
    Base class for all SciOS tools.

    Responsibilities
    ----------------
    - Define a common execution interface
    - Expose tool metadata
    """

    def __init__(
        self,
        name: str,
        description: str = "",
    ):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute the tool.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def metadata(self) -> Dict[str, Any]:
        """
        Return tool metadata.
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }

    def status(self) -> Dict[str, str]:
        """
        Return tool status.
        """
        return {
            "tool": self.name,
            "status": "ready",
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"