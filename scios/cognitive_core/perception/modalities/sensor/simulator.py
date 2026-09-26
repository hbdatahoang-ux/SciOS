"""Deterministic simulator sensor for the SciOS Cognitive Core."""

from __future__ import annotations

from typing import Any

from ...core.result import PerceptionResult
from ...core.types import Metadata, Modality, PerceptionStatus
from .base import SensorBase


class SimulatorSensor(SensorBase):
    """Deterministic sensor backed by an in-memory value."""

    value: Any

    def __init__(
        self,
        *,
        name: str,
        sensor_type: str,
        value: Any,
    ) -> None:
        """Initialize a simulator sensor with an initial value."""

        super().__init__(
            name=name,
            sensor_type=sensor_type,
        )

        self.value = value

    def read(self) -> Any:
        """Return the current simulated sensor value."""

        return self.value

    def set_value(self, value: Any) -> None:
        """Update the simulated sensor value."""

        self.value = value

    def perceive(
        self,
        raw_input: Any,
        metadata: Metadata | None = None,
    ) -> PerceptionResult:
        """Return the current simulated value as a perception result."""

        result_metadata = dict(metadata or {})
        result_metadata.update(
            {
                "sensor_type": self.sensor_type,
            }
        )

        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=Modality.SENSOR,
            content=self.read(),
            confidence=1.0,
            metadata=result_metadata,
        )


__all__ = ["SimulatorSensor"]