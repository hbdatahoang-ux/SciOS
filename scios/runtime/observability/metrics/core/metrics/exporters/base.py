# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

from abc import ABC, abstractmethod

import copy
import threading

from pathlib import Path

from typing import Any, Final, TypeAlias

from scios.runtime.observability.metrics.core.metrics.serialization.metric_serializer import (
    MetricSerializer,
)


Serializable: TypeAlias = Any
ExportPayload: TypeAlias = dict[str, Any]
ExportManyPayload: TypeAlias = list[ExportPayload]


DEFAULT_VERSION: Final[str] = "1.0"
DEFAULT_ENCODING: Final[str] = "utf-8"


__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "Serializable",
    "ExportPayload",
    "ExportManyPayload",
    "BaseExporter",
]

# ==========================================================
# Part 2. Constructor
# ==========================================================


class BaseExporter(ABC):
    """
    Base class for all metric exporters.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_serializer",
        "_lock",
    )

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        encoding: str = DEFAULT_ENCODING,
        serializer: MetricSerializer | None = None,
    ) -> None:
        self._version = version
        self._encoding = encoding
        self._serializer = serializer or MetricSerializer()
        self._lock = threading.RLock()


# ==========================================================
# Part 3. Properties
# ==========================================================

    @property
    def version(self) -> str:
        """Exporter version."""
        return self._version

    @property
    def encoding(self) -> str:
        """Default text encoding."""
        return self._encoding

    @property
    def serializer(self) -> MetricSerializer:
        """Underlying metric serializer."""
        return self._serializer

    @property
    def lock(self) -> threading.RLock:
        """Internal synchronization lock."""
        return self._lock

# ==========================================================
# Part 4. Internal Helpers
# ==========================================================

    def _metadata(self) -> dict[str, Any]:
        """
        Exporter metadata.
        """
        return {
            "version": self._version,
            "encoding": self._encoding,
            "exporter": self.__class__.__name__,
        }

    def _normalize(
        self,
        metric: Serializable,
    ) -> dict[str, Any]:
        """
        Normalize a metric object into a dictionary.
        """

        if isinstance(metric, dict):
            return copy.deepcopy(metric)

        if hasattr(metric, "to_dict"):
            return copy.deepcopy(metric.to_dict())

        return {
            "value": copy.deepcopy(metric),
        }

    def _export_payload(
        self,
        metric: Serializable,
    ) -> ExportPayload:
        """
        Build export payload.
        """

        return {
            "metadata": self._metadata(),
            "metric": self._normalize(metric),
        }

    def _export_many_payload(
        self,
        metrics: list[Serializable],
    ) -> ExportManyPayload:
        """
        Build payload for multiple metrics.
        """

        return [
            self._export_payload(metric)
            for metric in metrics
        ]


# ==========================================================
# Part 5. Abstract Export API
# ==========================================================

    @abstractmethod
    def export(
        self,
        metric: Serializable,
    ) -> Any:
        """
        Export a metric.
        """
        raise NotImplementedError

    @abstractmethod
    def export_many(
        self,
        metrics: list[Serializable],
    ) -> Any:
        """
        Export multiple metrics.
        """
        raise NotImplementedError

    @abstractmethod
    def export_bytes(
        self,
        metric: Serializable,
    ) -> bytes:
        """
        Export metric as bytes.
        """
        raise NotImplementedError

    @abstractmethod
    def export_many_bytes(
        self,
        metrics: list[Serializable],
    ) -> bytes:
        """
        Export multiple metrics as bytes.
        """
        raise NotImplementedError


# ==========================================================
# Part 6. File API
# ==========================================================

    def export_file(
        self,
        metric: Serializable,
        path: str | Path,
    ) -> Path:
        """
        Export a metric to file.
        """

        path = Path(path)

        path.write_bytes(
            self.export_bytes(metric),
        )

        return path

    def export_many_file(
        self,
        metrics: list[Serializable],
        path: str | Path,
    ) -> Path:
        """
        Export multiple metrics to file.
        """

        path = Path(path)

        path.write_bytes(
            self.export_many_bytes(metrics),
        )

        return path

    def load_file(
        self,
        path: str | Path,
    ) -> bytes:
        """
        Load exported file.
        """

        return Path(path).read_bytes()

# ==========================================================
# Part 7. Validation
# ==========================================================

    def validate(
        self,
    ) -> bool:
        """
        Validate exporter state.
        """

        if not isinstance(self._version, str):
            return False

        if not isinstance(self._encoding, str):
            return False

        if self._serializer is None:
            return False

        return True

    def is_valid(
        self,
    ) -> bool:
        """
        Safe validation.
        """

        try:
            return self.validate()
        except Exception:
            return False


# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"version={self._version!r}, "
            f"encoding={self._encoding!r})"
        )

    def __str__(
        self,
    ) -> str:

        return self.__repr__()

    def __len__(
        self,
    ) -> int:

        return 2

    def __bool__(
        self,
    ) -> bool:

        return self.validate()

    def __copy__(
        self,
    ) -> "BaseExporter":

        cls = self.__class__
        obj = cls.__new__(cls)
        obj.__setstate__(self.__getstate__())
        return obj

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "BaseExporter":

        cls = self.__class__
        obj = cls.__new__(cls)
        memo[id(self)] = obj
        obj.__setstate__(copy.deepcopy(self.__getstate__(), memo))
        return obj

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, self.__class__):
            return False

        return (
            self._version,
            self._encoding,
        ) == (
            other._version,
            other._encoding,
        )

    def __hash__(
        self,
    ) -> int:

        return hash(
            (
                self.__class__,
                self._version,
                self._encoding,
            )
        )

    def __getstate__(
        self,
    ) -> dict[str, Any]:

        return {
            "version": self._version,
            "encoding": self._encoding,
            "serializer": self._serializer,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._version = state["version"]
        self._encoding = state["encoding"]
        self._serializer = state["serializer"]
        self._lock = threading.RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "Serializable",
    "ExportPayload",
    "ExportManyPayload",
    "BaseExporter",
]                