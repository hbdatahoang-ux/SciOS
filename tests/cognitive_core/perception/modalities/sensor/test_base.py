"""Contract tests for the sensor base abstraction."""

from typing import Any

import pytest

from scios.cognitive_core.perception.core.base import BasePerceptor
from scios.cognitive_core.perception.core.types import Modality
from scios.cognitive_core.perception.modalities.sensor.base import (
    SensorBase,
)


class ConcreteSensor(SensorBase):
    """Concrete test implementation."""

    def read(self) -> Any:
        return {"value": 42}

    def perceive(
        self,
        raw_input: Any,
        metadata: dict[str, Any] | None = None,
    ):
        return raw_input


class StrictSensor(SensorBase):
    """Concrete sensor with a stricter validation rule."""

    def read(self) -> Any:
        return 1

    def validate(self, data: Any) -> None:
        if not isinstance(data, int):
            raise TypeError("sensor data must be an integer")

    def perceive(
        self,
        raw_input: Any,
        metadata: dict[str, Any] | None = None,
    ):
        return raw_input


def test_sensor_base_is_abstract() -> None:
    assert issubclass(SensorBase, BasePerceptor)

    with pytest.raises(TypeError):
        SensorBase(
            name="sensor",
            sensor_type="generic",
        )


def test_sensor_base_modality() -> None:
    sensor = ConcreteSensor(
        name="temperature",
        sensor_type="temperature",
    )

    assert sensor.modality is Modality.SENSOR


def test_sensor_name() -> None:
    sensor = ConcreteSensor(
        name="temperature",
        sensor_type="temperature",
    )

    assert sensor.name == "temperature"


def test_sensor_type() -> None:
    sensor = ConcreteSensor(
        name="temperature",
        sensor_type="temperature",
    )

    assert sensor.sensor_type == "temperature"


def test_sensor_read_contract() -> None:
    sensor = ConcreteSensor(
        name="temperature",
        sensor_type="temperature",
    )

    assert sensor.read() == {"value": 42}


def test_sensor_validate_accepts_non_none_data() -> None:
    sensor = ConcreteSensor(
        name="generic",
        sensor_type="generic",
    )

    sensor.validate({"value": 1})


def test_sensor_validate_rejects_none() -> None:
    sensor = ConcreteSensor(
        name="generic",
        sensor_type="generic",
    )

    with pytest.raises(ValueError, match="must not be None"):
        sensor.validate(None)


def test_sensor_type_must_be_non_empty() -> None:
    with pytest.raises(
        ValueError,
        match="sensor_type must be a non-empty string",
    ):
        ConcreteSensor(
            name="sensor",
            sensor_type="",
        )


def test_sensor_type_must_be_string() -> None:
    with pytest.raises(
        ValueError,
        match="sensor_type must be a non-empty string",
    ):
        ConcreteSensor(
            name="sensor",
            sensor_type=123,
        )


def test_sensor_name_contract_is_inherited() -> None:
    with pytest.raises(
        ValueError,
        match="name must be a non-empty string",
    ):
        ConcreteSensor(
            name="",
            sensor_type="generic",
        )


def test_sensor_name_must_be_string() -> None:
    with pytest.raises(
        ValueError,
        match="name must be a non-empty string",
    ):
        ConcreteSensor(
            name=123,
            sensor_type="generic",
        )


def test_sensor_perceive_remains_abstract() -> None:
    assert "perceive" in SensorBase.__abstractmethods__


def test_read_remains_abstract() -> None:
    assert "read" in SensorBase.__abstractmethods__


def test_subclass_can_override_validation() -> None:
    sensor = StrictSensor(
        name="strict",
        sensor_type="integer",
    )

    sensor.validate(10)

    with pytest.raises(
        TypeError,
        match="sensor data must be an integer",
    ):
        sensor.validate("10")


def test_sensor_base_exposes_expected_contract() -> None:
    assert hasattr(SensorBase, "read")
    assert hasattr(SensorBase, "validate")
    assert hasattr(SensorBase, "perceive")


def test_sensor_instances_are_perceptors() -> None:
    sensor = ConcreteSensor(
        name="generic",
        sensor_type="generic",
    )

    assert isinstance(sensor, BasePerceptor)
