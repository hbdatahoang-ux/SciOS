"""
SciOS Reasoning Backend
=======================

Abstract backend interface for the SciOS reasoning subsystem.

Every reasoning implementation (QTC, Symbolic, Neural, Hybrid,
etc.) should implement this interface.

The ReasoningEngine depends only on this abstraction, allowing
reasoning implementations to evolve independently.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ReasoningBackend(ABC):
    """
    Abstract reasoning backend.

    Concrete implementations are responsible for executing the
    actual reasoning algorithm.
    """

    # ==========================================================
    # Lifecycle
    # ==========================================================

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the backend.
        """

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the backend.
        """

    @abstractmethod
    def reset(self) -> None:
        """
        Reset backend state.
        """

    # ==========================================================
    # Reasoning
    # ==========================================================

    @abstractmethod
    def reason(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a reasoning request.

        Parameters
        ----------
        query:
            User query.

        context:
            Optional contextual information.

        Returns
        -------
        dict
            Structured reasoning result.
        """

    # ==========================================================
    # Runtime information
    # ==========================================================

    @abstractmethod
    def status(self) -> dict[str, Any]:
        """
        Return backend runtime status.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable backend name.
        """

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Backend version.
        """

    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """
        List supported reasoning capabilities.
        """
