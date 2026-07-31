"""
SciOS Cognitive Core Tool Base
================================

Base abstraction for cognitive tool execution.

Python 3.11+
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


__all__ = [
    "Tool",
]


class Tool(ABC):
    """
    Base Tool abstraction.

    Supports:

    - class-level metadata
    - instance metadata
    - validation
    - execution
    """

    name: str = "unnamed"

    description: str = ""


    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:

        # Preserve subclass class attributes

        if name is not None:

            self.name = name

        elif not getattr(
            self,
            "name",
            None,
        ):

            self.name = (
                self.__class__.__name__
            )


        if description is not None:

            self.description = description



    # ==================================================
    # Required APIs
    # ==================================================

    @abstractmethod
    def execute(
        self,
        request: Any,
    ) -> Any:
        """
        Execute tool request.
        """

        raise NotImplementedError



    # ==================================================
    # Validation
    # ==================================================

    def validate(
        self,
        request: Any,
    ) -> bool:
        """
        Validate request.

        Default accepts all requests.
        """

        return True



    # ==================================================
    # Metadata
    # ==================================================

    def info(
        self,
    ) -> dict[str, Any]:

        return {

            "name":
                self.name,

            "description":
                self.description,

            "type":
                self.__class__.__name__,

        }



    # ==================================================
    # Protocol
    # ==================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}"
            f"(name={self.name!r})"

        )