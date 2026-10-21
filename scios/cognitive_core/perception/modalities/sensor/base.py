"""Base sensor contract for the SciOS Cognitive Core."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...core.base import BasePerceptor
from ...core.types import Modality


class SensorBase(BasePerceptor, ABC):
    """Abstract base class for all sensor perception sources."""

    sensor_type: str

    def __init__(
        self,
        *,
        name: str,
        sensor_type: str,
    ) -> None:
        """Initialize a sensor with its identity and sensor type."""

        super().__init__(
            name=name,
            modality=Modality.SENSOR,
        )

        if not sensor_type or not isinstance(sensor_type, str):
            raise ValueError(
                "sensor_type must be a non-empty string"
            )

        self.sensor_type = sensor_type

    def validate(self, data: Any) -> None:
        """Validate sensor data."""

        if data is None:
            raise ValueError("sensor data must not be None")

    @abstractmethod
    def read(self) -> Any:
        """Read raw data from the sensor source."""

        raise NotImplementedError


__all__ = ["SensorBase"]
