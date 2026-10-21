# ==============================================================================
# SciOS Runtime Science
# Synthetic World
# ==============================================================================

from __future__ import annotations

from typing import Any, Mapping

from scios.runtime.science.experiment.models import Experiment

from .models import WorldResult, WorldState
from .rules import WorldRule


# ==============================================================================
# Synthetic World
# ==============================================================================


class SyntheticWorld:
    """
    Deterministic experimental world.

    Semantic boundary:

        ScientificExecutor
            ↓
        parameters
            ↓
        SyntheticWorld
            ↓
        WorldRule
            ↓
        WorldResult

    The world:

        - owns the evolving world state
        - owns registered rules
        - applies rules deterministically
        - produces WorldResult

    The world does not:

        - evaluate hypotheses
        - create observations
        - create execution results
        - interpret scientific meaning
        - mutate the Experiment
    """

    # ==========================================================================
    # Construction
    # ==========================================================================

    def __init__(
        self,
        rules: tuple[WorldRule, ...] = (),
        initial_state: WorldState | None = None,
    ) -> None:
        if not isinstance(rules, tuple):
            raise TypeError(
                "rules must be a tuple of WorldRule"
            )

        for rule in rules:
            self._validate_rule(rule)

        self._rules: list[WorldRule] = list(rules)
        self._state = (
            initial_state
            if initial_state is not None
            else WorldState()
        )

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def state(self) -> WorldState:
        """
        Current world state.
        """
        return self._state

    @property
    def rules(self) -> tuple[WorldRule, ...]:
        """
        Registered rules as an immutable public view.
        """
        return tuple(self._rules)

    # ==========================================================================
    # Rule Management
    # ==========================================================================

    def add_rule(
        self,
        rule: WorldRule,
    ) -> SyntheticWorld:
        """
        Register one deterministic world rule.

        Returns
        -------
        SyntheticWorld
            This world, allowing fluent construction.
        """

        self._validate_rule(rule)

        self._rules.append(rule)

        return self

    # ==========================================================================
    # Execution
    # ==========================================================================

    def run(
        self,
        parameters: Mapping[str, Any],
    ) -> WorldResult:
        """
        Execute the world using experiment parameters.

        This is the canonical world entry point used by
        ScientificExecutor.
        """

        if not isinstance(parameters, Mapping):
            raise TypeError(
                "parameters must be a mapping"
            )

        values: dict[str, Any] = {}

        state = self._state

        for rule in self._rules:
            result = rule.apply(
                state,
                parameters,
            )

            if not isinstance(result, WorldResult):
                raise TypeError(
                    "world rule must return WorldResult"
                )

            values.update(result.values)
            state = result.state

        self._state = state

        return WorldResult(
            values=values,
            state=state,
        )

    # ==========================================================================
    # Experiment Compatibility API
    # ==========================================================================

    def execute(
        self,
        experiment: Experiment | Mapping[str, Any],
    ) -> WorldResult:
        """
        Compatibility entry point accepting an Experiment.

        This method preserves the original SyntheticWorld API while
        delegating actual execution to run().
        """

        if isinstance(experiment, Experiment):
            return self.run(
                experiment.parameters,
            )

        if isinstance(experiment, Mapping):
            parameters = experiment.get("parameters")

            if not isinstance(parameters, Mapping):
                raise TypeError(
                    "experiment must provide mapping parameters"
                )

            return self.run(parameters)

        raise TypeError(
            "experiment must be an Experiment or mapping"
        )

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_rule(
        rule: WorldRule,
    ) -> None:
        if rule is None:
            raise TypeError(
                "rule must not be None"
            )

        if not hasattr(rule, "apply"):
            raise TypeError(
                "rule must provide apply()"
            )

    # ==========================================================================
    # Python Protocols
    # ==========================================================================

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self):
        return iter(self.rules)

    def __contains__(
        self,
        rule: WorldRule,
    ) -> bool:
        return rule in self._rules

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"rules={len(self._rules)}, "
            f"state={self._state!r}"
            f")"
        )


# ==============================================================================
# Public API
# ==============================================================================

__all__ = [
    "SyntheticWorld",
]