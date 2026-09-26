# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import copy
import json

from pathlib import Path
from threading import RLock
from typing import Any, Final, TypeAlias

from scios.runtime.observability.metrics.core.metrics.serialization.metric_serializer import (
    MetricSerializer,
)


Serializable: TypeAlias = Any


DEFAULT_VERSION: Final[str] = "1.0"
DEFAULT_ENCODING: Final[str] = "utf-8"
DEFAULT_SERVICE_NAME: Final[str] = "SciOS"
DEFAULT_SERVICE_NAMESPACE: Final[str] = "scios.metrics"


__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_SERVICE_NAME",
    "DEFAULT_SERVICE_NAMESPACE",
    "Serializable",
    "OpenTelemetryExporter",
]


class OpenTelemetryExporter:
    """
    OpenTelemetry-compatible exporter.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_service_name",
        "_service_namespace",
        "_serializer",
        "_lock",
    )

    # ==========================================================
    # Part 2. Constructor
    # ==========================================================

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        encoding: str = DEFAULT_ENCODING,
        service_name: str = DEFAULT_SERVICE_NAME,
        service_namespace: str = DEFAULT_SERVICE_NAMESPACE,
        serializer: MetricSerializer | None = None,
    ) -> None:
        """
        Create OpenTelemetry exporter.
        """

        self._version = version
        self._encoding = encoding
        self._service_name = service_name
        self._service_namespace = service_namespace

        self._serializer = (
            serializer
            if serializer is not None
            else MetricSerializer()
        )

        self._lock = RLock()

    # ==========================================================
    # Part 3. Properties
    # ==========================================================

    @property
    def version(self) -> str:
        """Exporter version."""
        return self._version

    @property
    def encoding(self) -> str:
        """Default encoding."""
        return self._encoding

    @property
    def service_name(self) -> str:
        """OpenTelemetry service name."""
        return self._service_name

    @property
    def service_namespace(self) -> str:
        """OpenTelemetry service namespace."""
        return self._service_namespace

    @property
    def serializer(self) -> MetricSerializer:
        """Underlying metric serializer."""
        return self._serializer

    @property
    def lock(self) -> RLock:
        """Internal synchronization lock."""
        return self._lock

    # ==========================================================
    # Part 4. Internal Helpers
    # ==========================================================

    def _metadata(self) -> dict[str, Any]:
        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "encoding": self._encoding,
            "service_name": self._service_name,
            "service_namespace": self._service_namespace,
        }

    def _normalize(
        self,
        obj: Any,
    ) -> dict[str, Any]:
        """
        Normalize object into plain dictionary.
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

        return {"value": data}

    def _resource_attributes(self) -> dict[str, Any]:
        """
        OpenTelemetry resource attributes.
        """

        return {
            "service.name": self._service_name,
            "service.namespace": self._service_namespace,
        }

    def _export_payload(
        self,
        obj: Any,
    ) -> dict[str, Any]:

        metric = self._normalize(obj)

        return {
            "resource": self._resource_attributes(),
            "scopeMetrics": [
                {
                    "metrics": [
                        metric,
                    ]
                }
            ],
            "metadata": self._metadata(),
        }

    def _export_many_payload(
        self,
        objects: list[Any] | tuple[Any, ...],
    ) -> dict[str, Any]:

        metrics = [
            self._normalize(obj)
            for obj in objects
        ]

        return {
            "resource": self._resource_attributes(),
            "scopeMetrics": [
                {
                    "metrics": metrics,
                }
            ],
            "metadata": self._metadata(),
            "count": len(metrics),
        }

    # ==========================================================
    # Part 5. Export API
    # ==========================================================

    def export(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:

        with self._lock:
            return self._export_payload(obj)

    def export_many(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> dict[str, Any]:

        with self._lock:
            return self._export_many_payload(objects)

    def export_otlp(
        self,
        obj: Serializable,
    ) -> bytes:
        """
        Export one object as OTLP-compatible payload.
        """

        with self._lock:

            payload = self._export_payload(obj)

            return json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
            ).encode(self._encoding)

    def export_many_otlp(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> bytes:
        """
        Export many objects as OTLP-compatible payload.
        """

        with self._lock:

            payload = self._export_many_payload(objects)

            return json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
            ).encode(self._encoding)

    # ==========================================================
    # Part 6. File Export
    # ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:

        with self._lock:

            file_path = Path(path)

            file_path.write_bytes(
                self.export_otlp(obj),
            )

            return file_path

    def export_many_file(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:

        with self._lock:

            file_path = Path(path)

            file_path.write_bytes(
                self.export_many_otlp(objects),
            )

            return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> bytes:

        with self._lock:

            file_path = Path(path)

            return file_path.read_bytes()

    # ==========================================================
    # Part 7. Validation
    # ==========================================================

    def validate(
        self,
        obj: Serializable,
    ) -> bool:
        """
        Validate whether an object can be exported.
        """

        try:
            self._normalize(obj)
            return True
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
            f"service_name={self._service_name!r}, "
            f"service_namespace={self._service_namespace!r}"
            f")"
        )

    def __str__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(v{self._version})"
        )

    def __len__(self) -> int:

        return 4

    def __bool__(self) -> bool:

        return True

    def __copy__(self):

        return self.__class__(
            version=self._version,
            encoding=self._encoding,
            service_name=self._service_name,
            service_namespace=self._service_namespace,
            serializer=self._serializer,
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ):

        copied = self.__class__(
            version=copy.deepcopy(
                self._version,
                memo,
            ),
            encoding=copy.deepcopy(
                self._encoding,
                memo,
            ),
            service_name=copy.deepcopy(
                self._service_name,
                memo,
            ),
            service_namespace=copy.deepcopy(
                self._service_namespace,
                memo,
            ),
            serializer=copy.deepcopy(
                self._serializer,
                memo,
            ),
        )

        memo[id(self)] = copied

        return copied

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            OpenTelemetryExporter,
        ):
            return NotImplemented

        return (
            self._version == other._version
            and self._encoding == other._encoding
            and self._service_name == other._service_name
            and self._service_namespace
            == other._service_namespace
        )

    def __hash__(self) -> int:

        return hash(
            (
                self._version,
                self._encoding,
                self._service_name,
                self._service_namespace,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "version": self._version,
            "encoding": self._encoding,
            "service_name": self._service_name,
            "service_namespace": self._service_namespace,
            "serializer": self._serializer,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._version = state["version"]
        self._encoding = state["encoding"]
        self._service_name = state["service_name"]
        self._service_namespace = state["service_namespace"]
        self._serializer = state["serializer"]
        self._lock = RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_SERVICE_NAME",
    "DEFAULT_SERVICE_NAMESPACE",
    "Serializable",
    "OpenTelemetryExporter",
]                    