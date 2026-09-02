"""Contract tests for the deterministic simulator sensor."""

from typing import Any

import pytest

from scios.cognitive_core.perception.core.result import PerceptionResult
from scios.cognitive_core.perception.core.types import (
    Modality,
    PerceptionStatus,
)
from scios.cognitive_core.perception.modalities.sensor.base import (
    SensorBase,
)
from scios.cognitive_core.perception.modalities.sensor.simulator import (
    SimulatorSensor,
)


def test_simulator_sensor_is_sensor_base() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    assert isinstance(sensor, SensorBase)


def test_simulator_sensor_modality() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    assert sensor.modality is Modality.SENSOR


def test_simulator_sensor_value() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    assert sensor.value == 25.0


def test_simulator_sensor_read_returns_value() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    assert sensor.read() == 25.0


def test_simulator_sensor_set_value() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    sensor.set_value(30.5)

    assert sensor.value == 30.5
    assert sensor.read() == 30.5


def test_simulator_sensor_accepts_any_value() -> None:
    payload = {"temperature": 25.0, "unit": "C"}

    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=payload,
    )

    assert sensor.read() == payload


def test_simulator_sensor_perceive_returns_result() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    result = sensor.perceive(None)

    assert isinstance(result, PerceptionResult)
    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.SENSOR
    assert result.content == 25.0


def test_simulator_sensor_perceive_uses_current_value() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    sensor.set_value(31.0)

    result = sensor.perceive(None)

    assert result.content == 31.0


def test_simulator_sensor_perceive_preserves_metadata() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    result = sensor.perceive(
        None,
        {"source": "simulation"},
    )

    assert result.metadata["source"] == "simulation"
    assert result.metadata["sensor_type"] == "temperature"


def test_simulator_sensor_confidence_is_one_for_success() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    result = sensor.perceive(None)

    assert result.confidence == 1.0


def test_simulator_sensor_has_deterministic_reads() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    assert sensor.read() == sensor.read()


def test_simulator_sensor_name_contract_is_inherited() -> None:
    with pytest.raises(
        ValueError,
        match="name must be a non-empty string",
    ):
        SimulatorSensor(
            name="",
            sensor_type="temperature",
            value=25.0,
        )


def test_simulator_sensor_type_contract_is_inherited() -> None:
    with pytest.raises(
        ValueError,
        match="sensor_type must be a non-empty string",
    ):
        SimulatorSensor(
            name="temperature",
            sensor_type="",
            value=25.0,
        )


def test_simulator_sensor_exposes_expected_contract() -> None:
    assert hasattr(SimulatorSensor, "read")
    assert hasattr(SimulatorSensor, "set_value")
    assert hasattr(SimulatorSensor, "perceive")


def test_simulator_sensor_perceive_does_not_depend_on_raw_input() -> None:
    sensor = SimulatorSensor(
        name="temperature",
        sensor_type="temperature",
        value=25.0,
    )

    result_a = sensor.perceive("ignored")
    result_b = sensor.perceive({"different": "input"})

    assert result_a.content == 25.0
    assert result_b.content == 25.0


def test_simulator_sensor_value_can_be_none() -> None:
    sensor = SimulatorSensor(
        name="optional",
        sensor_type="generic",
        value=None,
    )

    assert sensor.read() is None
