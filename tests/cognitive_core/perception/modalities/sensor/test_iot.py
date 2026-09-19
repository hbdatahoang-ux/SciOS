"""Contract tests for the IoT sensor implementation."""

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
from scios.cognitive_core.perception.modalities.sensor.iot import (
    IoTSensor,
)


def provider() -> dict[str, Any]:
    return {"temperature": 25.5, "unit": "C"}


def test_iot_sensor_is_sensor_base() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    assert isinstance(sensor, SensorBase)


def test_iot_sensor_modality() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    assert sensor.modality is Modality.SENSOR


def test_iot_sensor_endpoint() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    assert sensor.endpoint == "iot://sensor/temperature"


def test_iot_sensor_read_uses_provider() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    assert sensor.read() == {
        "temperature": 25.5,
        "unit": "C",
    }


def test_iot_sensor_perceive_returns_result() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    result = sensor.perceive(None)

    assert isinstance(result, PerceptionResult)
    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.SENSOR
    assert result.content == {
        "temperature": 25.5,
        "unit": "C",
    }


def test_iot_sensor_perceive_preserves_metadata() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    result = sensor.perceive(
        None,
        {"location": "lab"},
    )

    assert result.metadata["location"] == "lab"
    assert result.metadata["endpoint"] == "iot://sensor/temperature"
    assert result.metadata["sensor_type"] == "temperature"


def test_iot_sensor_confidence_is_one_for_success() -> None:
    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=provider,
    )

    result = sensor.perceive(None)

    assert result.confidence == 1.0


def test_iot_sensor_endpoint_must_be_non_empty() -> None:
    with pytest.raises(
        ValueError,
        match="endpoint must be a non-empty string",
    ):
        IoTSensor(
            name="temperature",
            sensor_type="temperature",
            endpoint="",
            provider=provider,
        )


def test_iot_sensor_endpoint_must_be_string() -> None:
    with pytest.raises(
        ValueError,
        match="endpoint must be a non-empty string",
    ):
        IoTSensor(
            name="temperature",
            sensor_type="temperature",
            endpoint=123,
            provider=provider,
        )


def test_iot_sensor_provider_must_be_callable() -> None:
    with pytest.raises(
        TypeError,
        match="provider must be callable",
    ):
        IoTSensor(
            name="temperature",
            sensor_type="temperature",
            endpoint="iot://sensor/temperature",
            provider=None,
        )


def test_iot_sensor_provider_failure_is_processing_error() -> None:
    def failing_provider() -> Any:
        raise RuntimeError("connection failed")

    sensor = IoTSensor(
        name="temperature",
        sensor_type="temperature",
        endpoint="iot://sensor/temperature",
        provider=failing_provider,
    )

    with pytest.raises(
        RuntimeError,
        match="connection failed",
    ):
        sensor.read()


def test_iot_sensor_provider_result_can_be_any_type() -> None:
    def numeric_provider() -> float:
        return 42.5

    sensor = IoTSensor(
        name="value",
        sensor_type="generic",
        endpoint="iot://sensor/value",
        provider=numeric_provider,
    )

    assert sensor.read() == 42.5


def test_iot_sensor_perceive_reads_provider_once() -> None:
    calls = 0

    def counted_provider() -> int:
        nonlocal calls
        calls += 1
        return 7

    sensor = IoTSensor(
        name="counter",
        sensor_type="counter",
        endpoint="iot://sensor/counter",
        provider=counted_provider,
    )

    result = sensor.perceive(None)

    assert calls == 1
    assert result.content == 7
