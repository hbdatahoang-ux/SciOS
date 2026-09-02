"""Contract tests for the ROS sensor implementation."""

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
from scios.cognitive_core.perception.modalities.sensor.ros import (
    RosSensor,
)


def provider() -> dict[str, Any]:
    return {"x": 1.0, "y": 2.0, "z": 3.0}


def test_ros_sensor_is_sensor_base() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    assert isinstance(sensor, SensorBase)


def test_ros_sensor_modality() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    assert sensor.modality is Modality.SENSOR


def test_ros_sensor_topic() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    assert sensor.topic == "/imu/data"


def test_ros_sensor_read_uses_provider() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    assert sensor.read() == {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
    }


def test_ros_sensor_perceive_returns_result() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    result = sensor.perceive(None)

    assert isinstance(result, PerceptionResult)
    assert result.status is PerceptionStatus.SUCCESS
    assert result.modality is Modality.SENSOR
    assert result.content == {
        "x": 1.0,
        "y": 2.0,
        "z": 3.0,
    }


def test_ros_sensor_perceive_preserves_metadata() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    result = sensor.perceive(
        None,
        {"frame_id": "base_link"},
    )

    assert result.metadata["frame_id"] == "base_link"
    assert result.metadata["topic"] == "/imu/data"
    assert result.metadata["sensor_type"] == "imu"


def test_ros_sensor_confidence_is_one_for_success() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    result = sensor.perceive(None)

    assert result.confidence == 1.0


def test_ros_sensor_topic_must_be_non_empty() -> None:
    with pytest.raises(
        ValueError,
        match="topic must be a non-empty string",
    ):
        RosSensor(
            name="imu",
            sensor_type="imu",
            topic="",
            provider=provider,
        )


def test_ros_sensor_topic_must_be_string() -> None:
    with pytest.raises(
        ValueError,
        match="topic must be a non-empty string",
    ):
        RosSensor(
            name="imu",
            sensor_type="imu",
            topic=123,
            provider=provider,
        )


def test_ros_sensor_provider_must_be_callable() -> None:
    with pytest.raises(
        TypeError,
        match="provider must be callable",
    ):
        RosSensor(
            name="imu",
            sensor_type="imu",
            topic="/imu/data",
            provider=None,
        )


def test_ros_sensor_provider_failure_propagates() -> None:
    def failing_provider() -> Any:
        raise RuntimeError("ROS source unavailable")

    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=failing_provider,
    )

    with pytest.raises(
        RuntimeError,
        match="ROS source unavailable",
    ):
        sensor.read()


def test_ros_sensor_provider_result_can_be_any_type() -> None:
    def numeric_provider() -> float:
        return 42.5

    sensor = RosSensor(
        name="value",
        sensor_type="generic",
        topic="/sensor/value",
        provider=numeric_provider,
    )

    assert sensor.read() == 42.5


def test_ros_sensor_perceive_reads_provider_once() -> None:
    calls = 0

    def counted_provider() -> int:
        nonlocal calls
        calls += 1
        return 7

    sensor = RosSensor(
        name="counter",
        sensor_type="counter",
        topic="/sensor/counter",
        provider=counted_provider,
    )

    result = sensor.perceive(None)

    assert calls == 1
    assert result.content == 7


def test_ros_sensor_does_not_require_ros2_runtime() -> None:
    sensor = RosSensor(
        name="imu",
        sensor_type="imu",
        topic="/imu/data",
        provider=provider,
    )

    assert sensor.topic == "/imu/data"
