"""Runtime governance adapter boundary for SciOS."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .context import GovernanceContext
from .exceptions import GovernanceError

if TYPE_CHECKING:
    from scios.runtime.tools.base import Tool

__all__ = ["GovernanceAdapter"]


class GovernanceAdapter(ABC):
    """Abstract runtime boundary for governance authorization."""

    @abstractmethod
    def authorize(
        self,
        governance_context: GovernanceContext,
        tool: Tool,
    ) -> None:
        """Authorize execution or raise GovernanceError.

        Normal return means ALLOW.

        Raising GovernanceError means DENY.

        Implementations must treat the supplied GovernanceContext as
        read-only and must not execute the tool or mutate execution data.
        """
        raise NotImplementedError
