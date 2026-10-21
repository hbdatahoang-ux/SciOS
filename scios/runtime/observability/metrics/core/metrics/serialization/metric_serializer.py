# ==========================================================
# Part 1. Imports & Constants
# ==========================================================

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Final, TypeAlias

from ..core.metric import Metric
from ..core.metric_snapshot import MetricSnapshot
from ..core.metric_hooks import MetricHooks
from ..core.registry import MetricRegistry
from ..core.collector import MetricCollector


Serializable: TypeAlias = (
    Metric
    | MetricSnapshot
    | MetricRegistry
    | MetricCollector
    | MetricHooks
    | dict[str, Any]
)

DEFAULT_VERSION: Final[str] = "1.0"
DEFAULT_ENCODING: Final[str] = "utf-8"

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "Serializable",
    "MetricSerializer",
]


# ==========================================================
# Part 2. Constructor
# ==========================================================

class MetricSerializer:
    """
    Thread-safe serializer for the SciOS Metrics subsystem.
    """

    VERSION: Final[str] = DEFAULT_VERSION
    ENCODING: Final[str] = DEFAULT_ENCODING

    __slots__ = (
        "_version",
        "_encoding",
        "_lock",
    )

    def __init__(
        self,
        *,
        version: str = DEFAULT_VERSION,
        encoding: str = DEFAULT_ENCODING,
    ) -> None:
        self._version = version
        self._encoding = encoding
        self._lock = RLock()


# ==========================================================
# Part 3. Properties
# ==========================================================

    @property
    def version(self) -> str:
        """
        Serializer version.
        """
        return self._version

    @property
    def encoding(self) -> str:
        """
        Default file encoding.
        """
        return self._encoding

    @property
    def lock(self) -> RLock:
        """
        Internal synchronization lock.
        """
        return self._lock

# ==========================================================
# Part 4. Internal Helpers
# ==========================================================

    def _base(self) -> dict[str, Any]:
        """
        Base serialization metadata.
        """
        return {
            "serializer": self.__class__.__name__,
            "version": self._version,
        }

    def _serialize_value(
        self,
        value: Any,
    ) -> Any:
        """
        Convert an arbitrary object into a JSON-serializable value.
        """

        if hasattr(value, "to_dict"):
            return value.to_dict()

        if hasattr(value, "snapshot"):
            return value.snapshot()

        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
                str,
                int,
                float,
                bool,
                type(None),
            ),
        ):
            return value

        return str(value)

    def _deserialize_value(
        self,
        value: Any,
    ) -> Any:
        """
        Internal payload extraction.
        """
        return value


# ==========================================================
# Part 5. Dict Serialization
# ==========================================================

    def serialize(
        self,
        obj: Any,
    ) -> dict[str, Any]:
        """
        Serialize object into dictionary.
        """

        with self._lock:
            return {
                **self._base(),
                "data": self._serialize_value(obj),
            }

    def serialize_metric(
        self,
        metric: Metric,
    ) -> dict[str, Any]:
        """
        Serialize Metric instance.
        """
        return self.serialize(metric)

    def serialize_snapshot(
        self,
        snapshot: MetricSnapshot | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Serialize snapshot.
        """
        return self.serialize(snapshot)

    def serialize_many(
        self,
        objects: list[Any] | tuple[Any, ...],
    ) -> dict[str, Any]:
        """
        Serialize multiple objects.
        """

        with self._lock:
            return {
                **self._base(),
                "count": len(objects),
                "items": [
                    self.serialize(obj)
                    for obj in objects
                ],
            }

    def to_dict(
        self,
        obj: Any,
    ) -> dict[str, Any]:
        """
        Convert object into dictionary.
        """
        return self.serialize(obj)


# ==========================================================
# Part 6. JSON Serialization
# ==========================================================

    def to_json(
        self,
        obj: Any,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize object into JSON.
        """

        return json.dumps(
            self.serialize(obj),
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=True,
            default=str,
        )

    def from_json(self, text: str) -> dict[str, Any]:
        payload = json.loads(text)
        return payload.get("data", payload)

    def many_to_json(
        self,
        objects: list[Any] | tuple[Any, ...],
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize multiple objects into JSON.
        """

        return json.dumps(
            self.serialize_many(objects),
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=True,
            default=str,
        )

# ==========================================================
# Part 7. File Serialization
# ==========================================================

    def save_json(
        self,
        obj: Any,
        path: str | Path,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Path:
        """
        Serialize object to a JSON file.
        """

        path = Path(path)

        with self._lock:
            path.write_text(
                self.to_json(
                    obj,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                ),
                encoding=self._encoding,
            )

        return path

    def load_json(self, path):
        with open(path, "r", encoding=self._encoding) as f:
            payload = json.load(f)

        return payload.get("data", payload)

    def __getstate__(self) -> dict[str, Any]:
        """
        Exclude runtime lock during pickling.
        """
        return {
            "_version": self._version,
            "_encoding": self._encoding,
        }


    def __setstate__(self, state: dict[str, Any]) -> None:
        """
        Restore runtime state after unpickling.
        """
        self._version = state["_version"]
        self._encoding = state["_encoding"]
        self._lock = RLock()        


# ==========================================================
# Part 8. Snapshot Serialization
# ==========================================================

    def create_snapshot(
        self,
        obj: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a serialization snapshot.
        """

        snapshot = {
            **self._base(),
            "type": obj.__class__.__name__,
            "snapshot": (
                obj.snapshot()
                if hasattr(obj, "snapshot")
                else self._serialize_value(obj)
            ),
        }

        if metadata is not None:
            snapshot["metadata"] = metadata

        return snapshot

    def snapshot_data(
        self,
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract snapshot payload.
        """

        return snapshot.get(
            "snapshot",
            {},
        )

    def clone_snapshot(
        self,
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Deep-copy snapshot.
        """

        return json.loads(
            json.dumps(
                snapshot,
                default=str,
            )
        )

    def restore_snapshot(
        self,
        snapshot: dict[str, Any],
        obj: Any,
    ) -> Any:
        """
        Restore object from snapshot.
        """

        payload = snapshot.get(
            "snapshot",
            snapshot,
        )

        if hasattr(obj, "restore"):
            obj.restore(payload)

        return obj


# ==========================================================
# Part 9. Validation
# ==========================================================

    def validate(self) -> bool:
        """
        Validate serializer configuration.
        """

        if not isinstance(
            self._version,
            str,
        ):
            raise TypeError(
                "version must be a string"
            )

        if not isinstance(
            self._encoding,
            str,
        ):
            raise TypeError(
                "encoding must be a string"
            )

        if not hasattr(
            self._lock,
            "acquire",
        ):
            raise TypeError(
                "lock is invalid"
            )

        return True

    def is_valid(self) -> bool:
        """
        Safe validation.
        """

        try:
            return self.validate()
        except Exception:
            return False

# ==========================================================
# Part 10. Python Protocols
# ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(version={self._version!r}, "
            f"encoding={self._encoding!r})"
        )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(version={self._version})"
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:
        return (
            isinstance(other, MetricSerializer)
            and self.version == other.version
            and self.encoding == other.encoding
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__class__,
                self._version,
                self._encoding,
            )
        )

    def __copy__(self):
        return self.__class__(
            version=self._version,
            encoding=self._encoding,
        )

    def __deepcopy__(
        self,
        memo,
    ):
        return self.__class__(
            version=self._version,
            encoding=self._encoding,
        )


# ==========================================================
# Part 11. Public API
# ==========================================================

__all__ = [
    "DEFAULT_VERSION",
    "DEFAULT_ENCODING",
    "Serializable",
    "MetricSerializer",
]                            