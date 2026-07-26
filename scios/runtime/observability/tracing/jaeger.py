"""
SciOS Observability - Jaeger Configuration
==========================================

Configuration helpers for exporting traces to Jaeger
through OpenTelemetry.

Jaeger is treated as a backend endpoint rather than
a standalone tracing implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "JaegerConfig",
]


@dataclass(slots=True)
class JaegerConfig:
    """
    Jaeger backend configuration.
    """

    endpoint: str = "http://localhost:4318"

    service_name: str = "SciOS"

    insecure: bool = True

    timeout: float = 10.0

    headers: dict[str, str] | None = None

    def to_dict(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "service_name": self.service_name,
            "insecure": self.insecure,
            "timeout": self.timeout,
            "headers": self.headers or {},
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)