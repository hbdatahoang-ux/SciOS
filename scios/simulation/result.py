from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .state import SimulationState


@dataclass(frozen=True)
class SimulationResult:
    """Generic result produced by a simulation run."""

    times: Sequence[float]
    states: Sequence[SimulationState]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if len(self.times) != len(self.states):
            raise ValueError("times and states must have the same length.")
