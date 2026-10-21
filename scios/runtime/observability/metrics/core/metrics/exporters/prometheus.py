# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any, Final, TypeAlias

from ..serialization.metric_serializer import MetricSerializer

Serializable: TypeAlias = Any

DEFAULT_VERSION: Final[str] = "1.0"
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_METRIC_PREFIX: Final[str] = ""
DEFAULT_INCLUDE_HELP: Final[bool] = True
DEFAULT_INCLUDE_TYPE: Final[bool] = True

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_METRIC_PREFIX",
    "DEFAULT_INCLUDE_HELP",
    "DEFAULT_INCLUDE_TYPE",
    "Serializable",
    "PrometheusExporter",
]


# ==========================================================
# Part 2. Constructor
# ==========================================================

class PrometheusExporter:
    """
    Prometheus text exposition exporter.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_metric_prefix",
        "_include_help",
        "_include_type",
        "_serializer",
        "_lock",
    )

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        encoding: str = DEFAULT_ENCODING,
        metric_prefix: str = DEFAULT_METRIC_PREFIX,
        include_help: bool = DEFAULT_INCLUDE_HELP,
        include_type: bool = DEFAULT_INCLUDE_TYPE,
        serializer: MetricSerializer | None = None,
    ) -> None:

        self._version = version
        self._encoding = encoding
        self._metric_prefix = metric_prefix
        self._include_help = include_help
        self._include_type = include_type
        self._serializer = serializer or MetricSerializer()
        self._lock = RLock()


# ==========================================================
# Part 3. Properties
# ==========================================================

    @property
    def version(self) -> str:
        return self._version

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def metric_prefix(self) -> str:
        return self._metric_prefix

    @property
    def include_help(self) -> bool:
        return self._include_help

    @property
    def include_type(self) -> bool:
        return self._include_type

    @property
    def serializer(self) -> MetricSerializer:
        return self._serializer

    @property
    def lock(self) -> RLock:
        return self._lock

# ==========================================================
# Part 4. Internal Helpers
# ==========================================================

    def _metadata(self) -> dict[str, Any]:
        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "encoding": self._encoding,
            "metric_prefix": self._metric_prefix,
            "include_help": self._include_help,
            "include_type": self._include_type,
        }

    def _normalize(
        self,
        obj: Any,
    ) -> dict[str, Any]:
        """
        Normalize object into a plain metric dictionary.
        """

        if isinstance(obj, dict):
            return dict(obj)

        if hasattr(obj, "to_dict"):
            return dict(obj.to_dict())

        if hasattr(obj, "snapshot"):
            snap = obj.snapshot()
            if isinstance(snap, dict):
                return dict(snap)

        data = self._serializer.to_dict(obj)

        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict):
                return dict(data["data"])
            return dict(data)

        return {
            "value": data,
        }

    def _metric_line(
        self,
        metric: Any,
    ) -> str:
        """
        Convert one metric into one Prometheus text line.
        """

        metric = self._normalize(metric)

        name = str(
            metric.get(
                "name",
                "metric",
            )
        )

        value = metric.get(
            "value",
            0,
        )

        labels = metric.get(
            "labels",
            {},
        )

        if labels:
            label_text = ",".join(
                f'{k}="{v}"'
                for k, v in labels.items()
            )
            return (
                f"{self._metric_prefix}"
                f"{name}"
                f"{{{label_text}}} "
                f"{value}"
            )

        return (
            f"{self._metric_prefix}"
            f"{name} "
            f"{value}"
        )

    def _export_payload(
        self,
        obj: Any,
    ) -> dict[str, Any]:

        metric = self._normalize(obj)

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "metric": metric,
            "text": self._metric_line(metric),
        }

    def _export_many_payload(
        self,
        objects: list[Any] | tuple[Any, ...],
    ) -> dict[str, Any]:

        items = [
            self._normalize(o)
            for o in objects
        ]

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "count": len(items),
            "items": items,
            "text": "\n".join(
                self._metric_line(item)
                for item in items
            ),
        }

# ==========================================================
# Part 5. Export API
# ==========================================================

    def export(
        self,
        obj: Serializable,
    ) -> str:
        """
        Export one metric in Prometheus exposition format.
        """

        with self._lock:
            return self._metric_line(obj)

    def export_many(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> str:
        """
        Export multiple metrics in Prometheus exposition format.
        """

        with self._lock:
            return "\n".join(
                self._metric_line(metric)
                for metric in objects
            )

    def export_text(
        self,
        obj: Serializable,
    ) -> str:
        """
        Alias of export().
        """

        return self.export(obj)

    def export_many_text(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> str:
        """
        Alias of export_many().
        """

        return self.export_many(objects)

# ==========================================================
# Part 6. File Export
# ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:
        """
        Export one metric to a Prometheus text file.
        """

        file_path = Path(path)

        with self._lock:

            file_path.write_text(
                self._metric_line(obj),
                encoding=self._encoding,
            )

        return file_path

    def export_many_file(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:
        """
        Export multiple metrics to a Prometheus text file.
        """

        file_path = Path(path)

        with self._lock:

            file_path.write_text(
                "\n".join(
                    self._metric_line(metric)
                    for metric in objects
                ),
                encoding=self._encoding,
            )

        return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> str:
        """
        Load Prometheus exposition text.
        """

        file_path = Path(path)

        with self._lock:
            return file_path.read_text(
                encoding=self._encoding,
            )


# ==========================================================
# Part 7. Validation
# ==========================================================

    def validate(
        self,
        obj: Serializable,
    ) -> bool:
        """
        Validate that an object can be exported.
        """

        try:
            metric = self._normalize(obj)

            return (
                isinstance(metric, dict)
                and "name" in metric
                and "value" in metric
            )

        except Exception:
            return False

    def is_valid(
        self,
        obj: Serializable,
    ) -> bool:
        """
        Alias of validate().
        """

        return self.validate(obj)

# ==========================================================
# Part 8. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"version={self._version!r}, "
            f"encoding={self._encoding!r}, "
            f"metric_prefix={self._metric_prefix!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return len(self._metadata())

    def __bool__(self) -> bool:
        return True

    def __copy__(self):
        return self.__class__(
            version=self._version,
            encoding=self._encoding,
            metric_prefix=self._metric_prefix,
            include_help=self._include_help,
            include_type=self._include_type,
        )

    def __deepcopy__(
        self,
        memo,
    ):
        return self.__class__(
            version=self._version,
            encoding=self._encoding,
            metric_prefix=self._metric_prefix,
            include_help=self._include_help,
            include_type=self._include_type,
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, self.__class__):
            return False

        return (
            self._version == other._version
            and self._encoding == other._encoding
            and self._metric_prefix == other._metric_prefix
            and self._include_help == other._include_help
            and self._include_type == other._include_type
        )

    def __hash__(self) -> int:
        return hash(
            (
                self._version,
                self._encoding,
                self._metric_prefix,
                self._include_help,
                self._include_type,
            )
        )


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_METRIC_PREFIX",
    "DEFAULT_INCLUDE_HELP",
    "DEFAULT_INCLUDE_TYPE",
    "Serializable",
    "PrometheusExporter",
]                            