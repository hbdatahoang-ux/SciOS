from __future__ import annotations

from typing import Any, Mapping

from scios.runtime.science.experiment.models import Experiment

from .models import WorldResult, WorldState
from .rules import WorldRule


class SyntheticWorld:
    """
    Deterministic experimental world.

    The world accepts an Experiment and applies its rules.
    """

    def __init__(
        self,
        rules: tuple[WorldRule, ...] = (),
        initial_state: WorldState | None = None,
    ) -> None:
        self._rules = tuple(rules)
        self._state = initial_state or WorldState()

    @property
    def state(self) -> WorldState:
        return self._state

    @property
    def rules(self) -> tuple[WorldRule, ...]:
        return self._rules

    def execute(
        self,
        experiment: Experiment,
    ) -> WorldResult:
        if not isinstance(experiment, Experiment):
            raise TypeError(
                "experiment must be an Experiment"
            )

        values: dict[str, Any] = {}
        state = self._state

        for rule in self._rules:
            result = rule.apply(
                state,
                experiment.parameters,
            )

            values.update(result.values)
            state = result.state

        self._state = state

        return WorldResult(
            values=values,
            state=state,
        )