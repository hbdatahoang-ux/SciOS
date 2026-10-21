"""IoT sensor implementation for the SciOS Cognitive Core."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ...core.result import PerceptionResult
from ...core.types import Metadata, Modality, PerceptionStatus
from .base import SensorBase


class IoTSensor(SensorBase):
    """Sensor implementation backed by an injected IoT data provider."""

    endpoint: str
    provider: Callable[[], Any]

    def __init__(
        self,
        *,
        name: str,
        sensor_type: str,
        endpoint: str,
        provider: Callable[[], Any],
    ) -> None:
        """Initialize an IoT sensor."""

        super().__init__(
            name=name,
            sensor_type=sensor_type,
        )

        if not endpoint or not isinstance(endpoint, str):
            raise ValueError(
                "endpoint must be a non-empty string"
            )

        if not callable(provider):
            raise TypeError("provider must be callable")

        self.endpoint = endpoint
        self.provider = provider

    def read(self) -> Any:
        """Read the current value from the injected IoT provider."""

        return self.provider()

    def perceive(
        self,
        raw_input: Any,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Read the IoT source and return a standardized result."""

        content = self.read()

        result_metadata = dict(metadata or {})
        result_metadata.update(
            {
                "endpoint": self.endpoint,
                "sensor_type": self.sensor_type,
            }
        )

        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=Modality.SENSOR,
            content=content,
            confidence=1.0,
            metadata=result_metadata,
        )


__all__ = ["IoTSensor"]