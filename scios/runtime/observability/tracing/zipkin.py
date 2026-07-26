"""
SciOS Observability - Zipkin Configuration
==========================================

Configuration model for exporting SciOS traces to Zipkin
through the OpenTelemetry exporter.

Design Goals
------------
- No dependency on OpenTelemetry SDK
- Pure configuration object
- Serializable
- Easy to validate
- Future-proof
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ZipkinConfig",
]


@dataclass(slots=True)
class ZipkinConfig:
    """
    Zipkin backend configuration.

    Parameters
    ----------
    endpoint:
        Zipkin collector endpoint.

    service_name:
        Service name shown in Zipkin UI.

    timeout:
        Export timeout (seconds).

    headers:
        Optional HTTP headers.

    enabled:
        Whether Zipkin export is enabled.
    """

    endpoint: str = "http://localhost:9411/api/v2/spans"

    service_name: str = "SciOS"

    timeout: float = 10.0

    headers: dict[str, str] = field(default_factory=dict)

    enabled: bool = True

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize configuration.
        """

        return {
            "endpoint": self.endpoint,
            "service_name": self.service_name,
            "timeout": self.timeout,
            "headers": dict(self.headers),
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ZipkinConfig":
        """
        Create configuration from dictionary.
        """

        return cls(
            endpoint=data.get(
                "endpoint",
                cls.endpoint,
            ),
            service_name=data.get(
                "service_name",
                cls.service_name,
            ),
            timeout=data.get(
                "timeout",
                cls.timeout,
            ),
            headers=data.get(
                "headers",
                {},
            ),
            enabled=data.get(
                "enabled",
                True,
            ),
        )

    # ======================================================
    # Helpers
    # ======================================================

    def validate(self) -> None:
        """
        Validate configuration.

        Raises
        ------
        ValueError
            If configuration is invalid.
        """

        if not self.endpoint:
            raise ValueError(
                "Zipkin endpoint cannot be empty."
            )

        if self.timeout <= 0:
            raise ValueError(
                "Timeout must be positive."
            )

    def copy(self) -> "ZipkinConfig":
        """
        Return a deep copy.
        """

        return ZipkinConfig(
            endpoint=self.endpoint,
            service_name=self.service_name,
            timeout=self.timeout,
            headers=dict(self.headers),
            enabled=self.enabled,
        )

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"service='{self.service_name}', "
            f"endpoint='{self.endpoint}', "
            f"enabled={self.enabled})"
        )