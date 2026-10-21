from __future__ import annotations

from typing import Any, Protocol

from .state import SimulationState


class SimulationModel(Protocol):
    """Scientific model defining how a simulation state evolves."""

    def derivative(
        self,
        state: SimulationState,
        time: float,
    ) -> Any:
        """Evaluate the state derivative at a given time."""
        ...
