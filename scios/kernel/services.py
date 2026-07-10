from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class KernelService(ABC):
    """
    KernelService = Abstract base class for all services managed by Kernel.
    """

    @abstractmethod
    def start(self) -> None:
        """
        Start the service.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """
        Stop the service.
        """
        raise NotImplementedError

    @abstractmethod
    def status(self) -> dict[str, Any]:
        """
        Return service status information.
        """
        raise NotImplementedError


# ----------------------------------------------------------
# Example concrete services
# ----------------------------------------------------------

class LoggingService(KernelService):
    """
    LoggingService = Example service for logging.
    """

    def __init__(self) -> None:
        self.active = False

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False

    def status(self) -> dict[str, Any]:
        return {"service": "logging", "active": self.active}


class MetricsService(KernelService):
    """
    MetricsService = Example service for metrics collection.
    """

    def __init__(self) -> None:
        self.active = False
        self.metrics: dict[str, Any] = {}

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False

    def status(self) -> dict[str, Any]:
        return {"service": "metrics", "active": self.active, "metrics": self.metrics}
