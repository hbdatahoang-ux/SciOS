# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import copy
import csv
import io
import threading

from pathlib import Path
from typing import Any, Final, TypeAlias

from ..serialization.metric_serializer import MetricSerializer


Serializable: TypeAlias = Any


DEFAULT_VERSION: Final[str] = "1.0"

DEFAULT_ENCODING: Final[str] = "utf-8"

DEFAULT_DELIMITER: Final[str] = ","

DEFAULT_QUOTECHAR: Final[str] = '"'


__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_DELIMITER",
    "DEFAULT_QUOTECHAR",
    "Serializable",
    "CSVExporter",
]

class CSVExporter:
    """
    CSV metric exporter.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_delimiter",
        "_quotechar",
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
        delimiter: str = DEFAULT_DELIMITER,
        quotechar: str = DEFAULT_QUOTECHAR,
        serializer: MetricSerializer | None = None,
    ) -> None:
        """
        Create CSV exporter.
        """

        self._version = version
        self._encoding = encoding
        self._delimiter = delimiter
        self._quotechar = quotechar

        self._serializer = (
            serializer
            if serializer is not None
            else MetricSerializer()
        )

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
        """Output encoding."""
        return self._encoding

    @property
    def delimiter(self) -> str:
        """CSV delimiter."""
        return self._delimiter

    @property
    def quotechar(self) -> str:
        """CSV quote character."""
        return self._quotechar

    @property
    def serializer(self) -> MetricSerializer:
        """Metric serializer."""
        return self._serializer

    @property
    def lock(self) -> Any:
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
            "delimiter": self._delimiter,
            "quotechar": self._quotechar,
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
            snapshot = obj.snapshot()
            if isinstance(snapshot, dict):
                return dict(snapshot)

        data = self._serializer.to_dict(obj)

        if isinstance(data, dict):
            payload = data.get("data")
            if isinstance(payload, dict):
                return dict(payload)
            return dict(data)

        return {"value": data}

    def _fieldnames(
        self,
        metrics: list[dict[str, Any]],
    ) -> list[str]:
        """
        Build stable CSV header.
        """

        fieldnames: list[str] = []

        for metric in metrics:
            for key in metric.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

        return fieldnames

    def _row(
        self,
        metric: dict[str, Any],
        fieldnames: list[str],
    ) -> dict[str, Any]:
        """
        Build one CSV row.
        """

        return {
            field: metric.get(field, "")
            for field in fieldnames
        }

    def _export_payload(
        self,
        obj: Any,
    ) -> dict[str, Any]:

        metric = self._normalize(obj)

        return {
            **self._metadata(),
            "data": metric,
        }

    def _export_many_payload(
        self,
        objects: list[Any] | tuple[Any, ...],
    ) -> dict[str, Any]:

        items = [
            self._normalize(obj)
            for obj in objects
        ]

        return {
            **self._metadata(),
            "count": len(items),
            "items": items,
        }


# ==========================================================
# Part 5. Export API
# ==========================================================

    def export(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Export one metric as structured payload.
        """

        with self._lock:
            return self._export_payload(obj)

    def export_many(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> dict[str, Any]:
        """
        Export multiple metrics as structured payload.
        """

        with self._lock:
            return self._export_many_payload(objects)

    def export_text(
        self,
        obj: Serializable,
    ) -> str:
        """
        Export one metric as CSV text.
        """

        with self._lock:

            metric = self._normalize(obj)
            fieldnames = self._fieldnames([metric])

            buffer = io.StringIO()

            writer = csv.DictWriter(
                buffer,
                fieldnames=fieldnames,
                delimiter=self._delimiter,
                quotechar=self._quotechar,
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )

            writer.writeheader()
            writer.writerow(
                self._row(
                    metric,
                    fieldnames,
                )
            )

            return buffer.getvalue()

    def export_many_text(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> str:
        """
        Export multiple metrics as CSV text.
        """

        with self._lock:

            metrics = [
                self._normalize(obj)
                for obj in objects
            ]

            buffer = io.StringIO()

            fieldnames = self._fieldnames(metrics)

            writer = csv.DictWriter(
                buffer,
                fieldnames=fieldnames,
                delimiter=self._delimiter,
                quotechar=self._quotechar,
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )

            writer.writeheader()

            for metric in metrics:
                writer.writerow(
                    self._row(
                        metric,
                        fieldnames,
                    )
                )

            return buffer.getvalue()


# ==========================================================
# Part 6. File Export
# ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:
        """
        Export one metric to CSV file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_text(
                self.export_text(obj),
                encoding=self._encoding,
            )

            return file_path

    def export_many_file(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:
        """
        Export multiple metrics to CSV file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_text(
                self.export_many_text(objects),
                encoding=self._encoding,
            )

            return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> str:
        """
        Load CSV text from file.
        """

        with self._lock:

            return Path(path).read_text(
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
        Validate whether an object can be exported.
        """

        try:
            self._export_payload(obj)
        except Exception:
            return False

        return True

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
            f"version={self.version!r}, "
            f"encoding={self.encoding!r}, "
            f"delimiter={self.delimiter!r}, "
            f"quotechar={self.quotechar!r}"
            f")"
        )

    def __str__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(v{self.version})"
        )

    def __len__(self) -> int:

        return 4

    def __bool__(self) -> bool:

        return True

    def __copy__(self):

        return self.__class__(
            version=self.version,
            encoding=self.encoding,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            serializer=self.serializer,
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ):

        copied = self.__class__(
            version=copy.deepcopy(self.version, memo),
            encoding=copy.deepcopy(self.encoding, memo),
            delimiter=copy.deepcopy(self.delimiter, memo),
            quotechar=copy.deepcopy(self.quotechar, memo),
            serializer=copy.deepcopy(self.serializer, memo),
        )

        memo[id(self)] = copied

        return copied

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, CSVExporter):
            return NotImplemented

        return (
            self.version == other.version
            and self.encoding == other.encoding
            and self.delimiter == other.delimiter
            and self.quotechar == other.quotechar
        )

    def __hash__(self) -> int:

        return hash(
            (
                self.version,
                self.encoding,
                self.delimiter,
                self.quotechar,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "version": self.version,
            "encoding": self.encoding,
            "delimiter": self.delimiter,
            "quotechar": self.quotechar,
            "serializer": self.serializer,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._version = state["version"]
        self._encoding = state["encoding"]
        self._delimiter = state["delimiter"]
        self._quotechar = state["quotechar"]
        self._serializer = state["serializer"]
        self._lock = threading.RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_DELIMITER",
    "DEFAULT_QUOTECHAR",
    "CSVExporter",
]