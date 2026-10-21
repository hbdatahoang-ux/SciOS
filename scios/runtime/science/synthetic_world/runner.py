from __future__ import annotations

from datetime import datetime, timezone

from scios.runtime.science.experiment.models import (
    Experiment,
    Observation,
)

from .world import SyntheticWorld


class SyntheticWorldRunner:
    """
    Execute scientific experiments against a synthetic world.
    """

    def __init__(self, world: SyntheticWorld) -> None:
        self.world = world

    def run(self, experiment: Experiment) -> Observation:
        result = self.world.execute(experiment)

        return Observation(
            id=f"O:{experiment.id}",
            experiment_id=experiment.id,
            values=result.values,
            observed_at=datetime.now(timezone.utc),
            metadata={
                "source": "synthetic_world",
            },
        )