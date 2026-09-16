"""
SciOS Agent Capability Contracts
================================

Minimal structural contracts required by the canonical Agent.

These protocols intentionally contain only the operations that
``scios.agents.base.Agent`` delegates.
"""

from __future__ import annotations

from typing import Any, Protocol


__all__ = [
    "MemoryCapability",
    "ToolRoutingCapability",
]


class MemoryCapability(Protocol):
    """
    Minimal memory capability required by the canonical Agent.
    """

    def store(
        self,
        key: str,
        value: Any,
    ) -> None:
        ...

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        ...


class ToolRoutingCapability(Protocol):
    """
    Minimal tool-routing capability required by the canonical Agent.
    """

    def route(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        ...
