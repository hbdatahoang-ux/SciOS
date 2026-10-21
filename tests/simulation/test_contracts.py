from __future__ import annotations

from dataclasses import dataclass

import pytest

from scios.simulation import (
    Integrator,
    SimulationModel,
    SimulationResult,
    SimulationState,
)


@dataclass
class DummyState:
    value: float

    def copy(self) -> "DummyState":
        return DummyState(self.value)


class DummyModel:
    def derivative(self, state: DummyState, time: float) -> float:
        return state.value


class DummyIntegrator:
    def step(
        self,
        model: DummyModel,
        state: DummyState,
        time: float,
        dt: float,
    ) -> DummyState:
        return DummyState(
            state.value + model.derivative(state, time) * dt
        )


def test_simulation_state_contract() -> None:
    state: SimulationState = DummyState(1.0)

    copied = state.copy()

    assert isinstance(copied, DummyState)
    assert copied is not state
    assert copied.value == 1.0


def test_simulation_model_contract() -> None:
    model: SimulationModel = DummyModel()
    state = DummyState(2.0)

    derivative = model.derivative(state, 0.5)

    assert derivative == 2.0


def test_integrator_contract() -> None:
    model: SimulationModel = DummyModel()
    integrator: Integrator = DummyIntegrator()
    state = DummyState(2.0)

    next_state = integrator.step(model, state, 0.0, 0.1)

    assert isinstance(next_state, DummyState)
    assert next_state.value == pytest.approx(2.2)


def test_simulation_result_contract() -> None:
    states = [DummyState(0.0), DummyState(1.0)]

    result = SimulationResult(
        times=[0.0, 1.0],
        states=states,
        metadata={"model": "dummy"},
    )

    assert list(result.times) == [0.0, 1.0]
    assert list(result.states) == states
    assert result.metadata["model"] == "dummy"


def test_simulation_result_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        SimulationResult(
            times=[0.0, 1.0],
            states=[DummyState(0.0)],
            metadata={},
        )
