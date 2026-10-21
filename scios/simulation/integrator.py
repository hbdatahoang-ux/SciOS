from __future__ import annotations

from typing import Protocol

from .model import SimulationModel
from .state import SimulationState


class Integrator(Protocol):
    """Numerical time-integration strategy."""

    def step(
        self,
        model: SimulationModel,
        state: SimulationState,
        time: float,
        dt: float,
    ) -> SimulationState:
        """Advance the state by one numerical time step."""
        ...
