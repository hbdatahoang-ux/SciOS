from __future__ import annotations

from typing import Protocol, Self


class SimulationState(Protocol):
    """Semantic state of a simulation at a point in its evolution."""

    def copy(self) -> Self:
        """Return an independent copy of the state."""
        ...
