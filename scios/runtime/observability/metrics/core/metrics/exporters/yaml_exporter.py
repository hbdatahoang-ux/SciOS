# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import copy
from pathlib import Path
from threading import RLock
from typing import Any, Final, TypeAlias

import yaml

from ..serialization.metric_serializer import MetricSerializer


Serializable: TypeAlias = Any


DEFAULT_VERSION: Final[str] = "1.0"

DEFAULT_ENCODING: Final[str] = "utf-8"

DEFAULT_SORT_KEYS: Final[bool] = False

DEFAULT_INDENT: Final[int] = 2

DEFAULT_ALLOW_UNICODE: Final[bool] = True


__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_INDENT",
    "DEFAULT_ALLOW_UNICODE",
    "Serializable",
    "YAMLExporter",
]


class YAMLExporter:
    """
    YAML metric exporter.
    """

    __slots__ = (
        "_version",
        "_encoding",
        "_sort_keys",
        "_indent",
        "_allow_unicode",
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
        sort_keys: bool = DEFAULT_SORT_KEYS,
        indent: int = DEFAULT_INDENT,
        allow_unicode: bool = DEFAULT_ALLOW_UNICODE,
        serializer: MetricSerializer | None = None,
    ) -> None:
        """
        Create YAML exporter.
        """

        self._version = version
        self._encoding = encoding
        self._sort_keys = sort_keys
        self._indent = indent
        self._allow_unicode = allow_unicode

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
        """Output encoding."""
        return self._encoding

    @property
    def indent(self) -> int:
        """YAML indentation."""
        return self._indent

    @property
    def sort_keys(self) -> bool:
        """Sort YAML keys."""
        return self._sort_keys

    @property
    def allow_unicode(self) -> bool:
        """Allow unicode output."""
        return self._allow_unicode

    @property
    def serializer(self) -> MetricSerializer:
        """Metric serializer."""
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
            "sort_keys": self._sort_keys,
            "indent": self._indent,
            "allow_unicode": self._allow_unicode,
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

    def _yaml_kwargs(self) -> dict[str, Any]:
        """
        Keyword arguments passed to yaml.safe_dump().
        """

        return {
            "sort_keys": self._sort_keys,
            "indent": self._indent,
            "allow_unicode": self._allow_unicode,
        }

    def _export_payload(
        self,
        obj: Any,
    ) -> dict[str, Any]:

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "data": self._normalize(obj),
        }

    def _export_many_payload(
        self,
        objects: list[Any] | tuple[Any, ...],
    ) -> dict[str, Any]:

        return {
            "exporter": self.__class__.__name__,
            "version": self._version,
            "count": len(objects),
            "items": [
                self._normalize(obj)
                for obj in objects
            ],
        }


# ==========================================================
# Part 5. Export API
# ==========================================================

    def export(
        self,
        obj: Serializable,
    ) -> dict[str, Any]:
        """
        Export one object as structured payload.
        """

        with self._lock:
            return self._export_payload(obj)

    def export_many(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> dict[str, Any]:
        """
        Export multiple objects as structured payload.
        """

        with self._lock:
            return self._export_many_payload(objects)

    def export_yaml(
        self,
        obj: Serializable,
    ) -> str:
        """
        Export one object as YAML.
        """

        with self._lock:
            return yaml.safe_dump(
                self._export_payload(obj),
                **self._yaml_kwargs(),
            )

    def export_many_yaml(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
    ) -> str:
        """
        Export multiple objects as YAML.
        """

        with self._lock:
            return yaml.safe_dump(
                self._export_many_payload(objects),
                **self._yaml_kwargs(),
            )


# ==========================================================
# Part 6. File Export
# ==========================================================

    def export_file(
        self,
        obj: Serializable,
        path: str | Path,
    ) -> Path:
        """
        Export one object to a YAML file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_text(
                self.export_yaml(obj),
                encoding=self._encoding,
            )

            return file_path

    def export_many_file(
        self,
        objects: list[Serializable] | tuple[Serializable, ...],
        path: str | Path,
    ) -> Path:
        """
        Export multiple objects to a YAML file.
        """

        with self._lock:

            file_path = Path(path)

            file_path.write_text(
                self.export_many_yaml(objects),
                encoding=self._encoding,
            )

            return file_path

    def load_file(
        self,
        path: str | Path,
    ) -> dict[str, Any]:
        """
        Load exported YAML file.
        """

        with self._lock:

            file_path = Path(path)

            data = yaml.safe_load(
                file_path.read_text(
                    encoding=self._encoding,
                )
            )

            return {} if data is None else dict(data)

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
            f"indent={self.indent!r}, "
            f"sort_keys={self.sort_keys!r}, "
            f"allow_unicode={self.allow_unicode!r}"
            f")"
        )

    def __str__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(v{self.version})"
        )

    def __len__(self) -> int:

        return 5

    def __bool__(self) -> bool:

        return True

    def __copy__(self):

        return self.__class__(
            version=self.version,
            encoding=self.encoding,
            indent=self.indent,
            sort_keys=self.sort_keys,
            allow_unicode=self.allow_unicode,
            serializer=self.serializer,
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ):

        copied = self.__class__(
            version=copy.deepcopy(self.version, memo),
            encoding=copy.deepcopy(self.encoding, memo),
            indent=copy.deepcopy(self.indent, memo),
            sort_keys=copy.deepcopy(self.sort_keys, memo),
            allow_unicode=copy.deepcopy(self.allow_unicode, memo),
            serializer=copy.deepcopy(self.serializer, memo),
        )

        memo[id(self)] = copied

        return copied

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(other, YAMLExporter):
            return NotImplemented

        return (
            self.version == other.version
            and self.encoding == other.encoding
            and self.indent == other.indent
            and self.sort_keys == other.sort_keys
            and self.allow_unicode == other.allow_unicode
        )

    def __hash__(self) -> int:

        return hash(
            (
                self.version,
                self.encoding,
                self.indent,
                self.sort_keys,
                self.allow_unicode,
            )
        )

    def __getstate__(self) -> dict[str, Any]:

        return {
            "version": self.version,
            "encoding": self.encoding,
            "indent": self.indent,
            "sort_keys": self.sort_keys,
            "allow_unicode": self.allow_unicode,
            "serializer": self.serializer,
        }

    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:

        self._version = state["version"]
        self._encoding = state["encoding"]
        self._indent = state["indent"]
        self._sort_keys = state["sort_keys"]
        self._allow_unicode = state["allow_unicode"]
        self._serializer = state["serializer"]
        self._lock = RLock()


# ==========================================================
# Part 9. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "DEFAULT_SORT_KEYS",
    "DEFAULT_INDENT",
    "DEFAULT_ALLOW_UNICODE",
    "Serializable",
    "YAMLExporter",
]            